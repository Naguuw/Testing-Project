# Pembuatan driver browser: Chrome/Chromium/Brave, Firefox, dan Edge.
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as OpsiChrome
from selenium.webdriver.chrome.service import Service as LayananChrome
from selenium.webdriver.edge.options import Options as OpsiEdge
from selenium.webdriver.edge.service import Service as LayananEdge
from selenium.webdriver.firefox.options import Options as OpsiFirefox
from selenium.webdriver.firefox.service import Service as LayananFirefox

from .konfigurasi import Konfigurasi, ambil_benar

NAMA_BINER = {
    "chrome": ("google-chrome", "chromium", "chromium-browser", "brave", "brave-browser"),
    "firefox": ("firefox", "firefox-esr"),
    "edge": ("microsoft-edge", "microsoft-edge-stable", "msedge"),
}
TEMPAT_BINER = {
    "chrome": (
        Path("/opt/brave-origin-bin/brave"),
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
    ),
    "firefox": (
        Path.home() / ".local/opt/firefox/firefox",
        Path("C:/Program Files/Mozilla Firefox/firefox.exe"),
        Path("C:/Program Files (x86)/Mozilla Firefox/firefox.exe"),
    ),
    "edge": (
        Path.home() / ".local/opt/microsoft-edge/msedge",
        Path("/opt/microsoft-edge/msedge"),
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    ),
}
TEMPAT_DRIVER = {
    "chrome": (
        Path.home() / ".cache/selenium/chromedriver/linux64/chromedriver",
        Path.home() / ".cache/selenium/chromedriver/win64/chromedriver.exe",
        Path("/usr/bin/chromedriver"),
    ),
    "firefox": (
        Path.home() / ".cache/selenium/geckodriver",
        Path.home() / ".cache/selenium/geckodriver.exe",
        Path("/usr/bin/geckodriver"),
    ),
    "edge": (
        Path.home() / ".cache/selenium/msedgedriver",
        Path.home() / ".cache/selenium/msedgedriver.exe",
        Path("/usr/bin/msedgedriver"),
    ),
}


# Chrome dan Edge berbasis Chromium, jadi setelan window-nya sama.
FLAG_CHROMIUM = (
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-dev-shm-usage",
    "--window-size=1366,768",
    "--lang=id-ID",
)


@dataclass(frozen=True)
class ProfilBrowser:
    nama: str
    biner: str | None
    driver: str | None


def cari_biner(nama: str, konf: Konfigurasi) -> str | None:
    # Urutan pencarian browser: .env, PATH, lalu lokasi umum.
    dari_env = konf.biner.get(nama, "")
    if dari_env:
        return dari_env
    for nama_biner in NAMA_BINER[nama]:
        ditemukan = shutil.which(nama_biner)
        if ditemukan:
            return ditemukan
    for kandidat in TEMPAT_BINER[nama]:
        if kandidat.exists():
            return str(kandidat)
    return None


def cari_driver(nama: str, konf: Konfigurasi) -> str | None:
    # Urutan pencarian driver: .env, lokasi umum, lalu Selenium Manager.
    dari_env = konf.driver.get(nama, "")
    if dari_env:
        return dari_env
    for kandidat in TEMPAT_DRIVER[nama]:
        if kandidat.exists():
            return str(kandidat)
    return None


def _opsi_kromium(konf: Konfigurasi, biner: str | None) -> OpsiChrome:
    opsi = OpsiChrome()
    if biner:
        opsi.binary_location = biner
    if konf.headless:
        opsi.add_argument("--headless=new")
    if ambil_benar("NO_SANDBOX", False):
        opsi.add_argument("--no-sandbox")
    for flag in FLAG_CHROMIUM:
        opsi.add_argument(flag)
    return opsi


def _opsi_edge(konf: Konfigurasi, biner: str | None) -> OpsiEdge:
    opsi = OpsiEdge()
    if biner:
        opsi.binary_location = biner
    if konf.headless:
        opsi.add_argument("--headless=new")
    if ambil_benar("NO_SANDBOX", False):
        opsi.add_argument("--no-sandbox")
    for flag in FLAG_CHROMIUM:
        opsi.add_argument(flag)
    return opsi


def _opsi_firefox(konf: Konfigurasi, biner: str | None) -> OpsiFirefox:
    opsi = OpsiFirefox()
    if biner:
        opsi.binary_location = biner
    if konf.headless:
        opsi.add_argument("--headless")
    opsi.add_argument("--width=1366")
    opsi.add_argument("--height=768")
    opsi.set_preference("intl.accept_languages", "id-ID,id")
    opsi.set_preference("browser.download.folderList", 2)
    opsi.set_preference("browser.download.dir", str(konf.folder_hasil))
    return opsi


def buat_driver(konf: Konfigurasi, profil: ProfilBrowser) -> webdriver.RemoteWebDriver:
    # Driver diambil dari lokasi yang tersedia, kalau tidak ada andalkan Selenium Manager.
    if profil.nama == "firefox":
        layanan = LayananFirefox(profil.driver) if profil.driver else LayananFirefox()
        return webdriver.Firefox(service=layanan, options=_opsi_firefox(konf, profil.biner))
    if profil.nama == "edge":
        layanan = LayananEdge(profil.driver) if profil.driver else LayananEdge()
        return webdriver.Edge(service=layanan, options=_opsi_edge(konf, profil.biner))

    layanan = LayananChrome(profil.driver) if profil.driver else LayananChrome()
    return webdriver.Chrome(service=layanan, options=_opsi_kromium(konf, profil.biner))


def profil_browser(nama: str, konf: Konfigurasi) -> ProfilBrowser:
    return ProfilBrowser(
        nama=nama,
        biner=cari_biner(nama, konf),
        driver=cari_driver(nama, konf),
    )


def tutup_driver(driver) -> None:
    try:
        driver.quit()
    except Exception:
        pass
