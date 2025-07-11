# ngx_waf_ipv64_block_script

## 🇩🇪 Beschreibung

**Technische Kurzbeschreibung**  
Dieses Skript automatisiert den Abruf und die Aufbereitung von IP-Blocklisten, die von [ipv64.net](https://ipv64.net/) bereitgestellt werden. Die Blocklisten enthalten bekannte schädliche, missbräuchliche oder unerwünschte IP-Adressen (z. B. Spamhaus, TOR-Exit-Nodes, Botnetze oder länderspezifische IP-Bereiche).

Das Skript lädt die Listen automatisch herunter, filtert und bereinigt die Einträge, entfernt Duplikate sowie überlappende Netzbereiche und speichert die finalen Adressen getrennt als **IPv4**-Listen. Diese Listen werden anschließend automatisch in das Verzeichnis einer **selbst kompilierten NGINX Web Application Firewall (ngx_waf)** kopiert.

Zum Abschluss wird der selbst kompilierte NGINX-Webserver neu geladen, um sicherzustellen, dass die aktuellen Sperrlisten eingebunden sind.

**Zweck**  
Durch die Integration der aktuellen Blocklisten von [ipv64.net](https://ipv64.net/) soll die Sicherheit der Webserver-Infrastruktur **unterstützt** werden. Dieses Skript kann helfen, die eigene Webseite etwas sicherer zu machen – es gibt jedoch **keine Garantie**, dass Angriffe vollständig blockiert werden können, da Umgehungen jederzeit möglich sind.

Dieses Setup basiert auf einem **angepassten Fork** von [ngx_waf](https://github.com/ADD-SP/ngx_waf) und meinem eigenen angepassten Fork: [https://github.com/Easton97-Jens/ngx_waf/tree/current](https://github.com/Easton97-Jens/ngx_waf/tree/current).  
Die Nutzung erfolgt **auf eigene Gefahr** – es wird keine Haftung übernommen.

Ich selbst bin **kein professioneller Programmierer**, daher freue ich mich über Verbesserungsvorschläge, Tipps oder Pull Requests von der Community – aber bitte nur auf **Deutsch**, da ich keine anderen Sprachen sprechen kann.

---

## 🇬🇧 Description

**Technical Overview**  
This script automates the retrieval and processing of IP blocklists provided by [ipv64.net](https://ipv64.net/). These blocklists include known malicious, abusive, or unwanted IP addresses (e.g., Spamhaus, TOR exit nodes, botnets, or country-specific IP ranges).

The script automatically downloads the lists, filters and cleans the entries, removes duplicates and overlapping networks, and saves the final addresses as separate **IPv4** files. These lists are then automatically copied to the directory of a **self-compiled NGINX Web Application Firewall (ngx_waf)**.

Finally, the self-compiled NGINX web server is reloaded to ensure the current blocklists are in use.

**Purpose**  
By integrating up-to-date blocklists from [ipv64.net](https://ipv64.net/), this script is intended to **help** make the server infrastructure a bit more secure. However, **there is no guarantee** that attacks can be fully blocked, as bypassing is always possible.

This setup is based on a **custom fork** of [ngx_waf](https://github.com/ADD-SP/ngx_waf) and my own adapted fork: [https://github.com/Easton97-Jens/ngx_waf/tree/current](https://github.com/Easton97-Jens/ngx_waf/tree/current).  
**Use at your own risk** – no warranty or liability is provided.

⚠️ **Please note:** I only speak German, so I can only review posts, issues or pull requests **written in German**.

---

## ✨ Hinweis / Note

📌 *Dieser Text und das Skript wurden mit Hilfe von **ChatGPT** (Künstliche Intelligenz von OpenAI) generiert.*  
📌 *This text and the script were generated with the help of **ChatGPT** (Artificial Intelligence by OpenAI).*
