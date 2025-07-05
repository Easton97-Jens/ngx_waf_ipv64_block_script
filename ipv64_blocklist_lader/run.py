import os
import subprocess
import sys

VENV_DIR = "venv"

def create_venv():
    print("📦 Erstelle virtuelle Umgebung ...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

def install_requirements():
    print("🔧 Installiere Abhängigkeiten in der venv ...")
    pip_executable = os.path.join(VENV_DIR, "bin", "pip")
    subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)

def run_downloader():
    print("🚀 Starte IP-Downloader ...")
    python_executable = os.path.join(VENV_DIR, "bin", "python")
    subprocess.run([python_executable, "ip_downloader.py"], check=True)

def main():
    if not os.path.isdir(VENV_DIR):
        create_venv()

    # IMMER sicherstellen, dass requirements installiert sind:
    install_requirements()

    run_downloader()

main()
