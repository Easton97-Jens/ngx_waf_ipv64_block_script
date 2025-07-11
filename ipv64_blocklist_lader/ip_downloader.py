import asyncio
import aiohttp
import ipaddress
import logging
from logging.handlers import RotatingFileHandler
from tqdm.asyncio import tqdm
from datetime import datetime
import colorlog
import shutil
import subprocess

CONFIG_FILE = "config.txt"
MAX_CONNECTIONS = 3
MAX_RETRIES = 5
GLOBAL_SLEEP = 1  # Sekunde Pause nach jedem Link
BACKOFF_BASE = 5  # Sekunden für Exponential Backoff

# === Logging Setup ===

color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s]%(reset)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

console_handler = colorlog.StreamHandler()
console_handler.setFormatter(color_formatter)
console_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "full.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))
file_handler.setLevel(logging.DEBUG)

error_handler = RotatingFileHandler(
    "errors.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
)
error_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))
error_handler.setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console_handler, file_handler, error_handler]
)

logger = logging.getLogger("ip_downloader")

# === Fehlschlag-Liste ===
failed_links = []


def load_links(config_file):
    with open(config_file, "r") as f:
        links = [line.strip() for line in f if line.strip()]
    return links


def clean_line(line):
    return line.split('#')[0].strip()


def is_valid_network(network):
    try:
        net_obj = ipaddress.ip_network(network, strict=False)
        if net_obj.version == 4:
            return True
    except ValueError:
        return False
    return False


async def fetch(session, url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(
                url,
                timeout=30,
                headers={"User-Agent": "MyBlocklistFetcher/1.0"}
            ) as response:
                response.raise_for_status()
                logger.info(f"✅ Erfolgreich geladen: {url}")
                return await response.text()
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                wait_time = BACKOFF_BASE * (2 ** (attempt - 1))
                logger.warning(
                    f"429 Too Many Requests bei {url} (Versuch {attempt}/{MAX_RETRIES}) — warte {wait_time}s ..."
                )
                await asyncio.sleep(wait_time)
            else:
                logger.warning(f"Fehler bei {url} (Versuch {attempt}/{MAX_RETRIES}): {e}")
        except Exception as e:
            logger.warning(f"Fehler bei {url} (Versuch {attempt}/{MAX_RETRIES}): {e}")

    logger.error(f"⛔️ Endgültig gescheitert: {url}")
    failed_links.append(url)
    return ""


async def bounded_fetch(sem, session, url):
    async with sem:
        result = await fetch(session, url)
        await asyncio.sleep(GLOBAL_SLEEP)
        return result


async def download_all(links):
    ipv4_list = []
    total_lines = 0

    sem = asyncio.Semaphore(MAX_CONNECTIONS)
    connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [bounded_fetch(sem, session, link) for link in links]
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="⬇️ Lade Listen"):
            content = await coro
            lines = content.splitlines()
            total_lines += len(lines)
            for line in lines:
                network = clean_line(line)
                if network and is_valid_network(network):
                    ipv4_list.append(network)

    return ipv4_list, total_lines


def remove_overlaps(networks):
    ip_objs = [ipaddress.ip_network(n, strict=False) for n in networks]
    collapsed = ipaddress.collapse_addresses(ip_objs)
    unique = sorted(str(net) for net in collapsed)
    return unique


def save_networks(networks, filename):
    with open(filename, "w") as f:
        for net in networks:
            f.write(net + "\n")
    logger.info(f"💾 {len(networks)} Netzwerke gespeichert in {filename}")


def main():
    links = load_links(CONFIG_FILE)
    if not links:
        logger.error("⚠️ Keine Links in config.txt gefunden!")
        return

    ipv4_list, total_lines = asyncio.run(download_all(links))

    logger.info(f"➡️ Gesamt geladene Zeilen (vor Filter): {total_lines}")

    before4 = len(ipv4_list)

    ipv4_list = remove_overlaps(ipv4_list)

    removed4 = before4 - len(ipv4_list)

    logger.info(f"🧹 Überlappungen/Redundanzen IPv4 entfernt: {removed4}")

    save_networks(ipv4_list, "ipv4_unique.txt")

    logger.info(f"✅ Final IPv4: {len(ipv4_list)}")

    if failed_links:
        with open("failed_links.txt", "w") as f:
            for link in failed_links:
                f.write(link + "\n")
        logger.warning(
            f"❌ {len(failed_links)} Links endgültig gescheitert — gespeichert in failed_links.txt"
        )
    else:
        logger.info("✅ Keine gescheiterten Links!")

    # === Zusammenfassung speichern ===
    summary = f"""
Run abgeschlossen: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

➡️ Gesamt geladene Zeilen: {total_lines}
🧹 Überlappungen/Redundanzen IPv4 entfernt: {removed4}

💾 IPv4 gespeichert: {len(ipv4_list)}

❌ Gescheiterte Links: {len(failed_links)}

Alles OK!
"""
    with open("summary.txt", "w") as f:
        f.write(summary.strip())
    logger.info("📄 Zusammenfassung geschrieben: summary.txt")

    # === Liste in WAF-Ordner kopieren ===
    dest_ipv4 = "/nginx_custom/nginx/ngx_waf/ipv4"

    shutil.copyfile("ipv4_unique.txt", dest_ipv4)
    logger.info(f"📂 IPv4-Liste nach {dest_ipv4} kopiert")

    # === Nginx neu laden ===
    try:
        subprocess.run(["nginx", "-s", "reload"], check=True)
        logger.info("🔄 Nginx erfolgreich neu geladen!")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Fehler beim Nginx-Reload: {e}")

    logger.info("🚀 Run fertig — bis morgen! Alles gut gespeichert!")

main()
