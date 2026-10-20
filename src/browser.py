"""Pembuatan driver browser untuk pengujian otomatis."""

from __future__ import annotations

import shutil
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from .konfigurasi import Konfigurasi, ambil_benar

NAMA_BINER = ("google-chrome", "chromium", "chromium-browser", "brave", "brave-browser")
TEMPAT_DRIVER = (
    Path.home() / ".cache/selenium/chromedriver/linux64/chromedriver",
    Path("/usr/bin/chromedriver"),
)


def cari_biner(konf: Konfigurasi) -> str | None:
    if konf.biner_peramban:
        return konf.biner_peramban
    for nama in NAMA_BINER:
        ditemukan = shutil.which(nama)
        if ditemukan:
            return ditemukan
    return None


def cari_driver(konf: Konfigurasi) -> str | None:
    if konf.driver_biner:
        return konf.driver_biner
    for kandidat in TEMPAT_DRIVER:
        if kandidat.exists():
            return str(kandidat)
    return None


def buat_driver(konf: Konfigurasi) -> webdriver.Chrome:
    """Buka browser Chrome (atau Brave/Chromium) dengan driver yang tersedia."""
    if konf.peramban not in {"chrome", "chromium", "brave"}:
        raise ValueError(
            f"Peramban '{konf.peramban}' belum didukung untuk otomasi. "
            "Pengujian otomatis memakai Chrome, Chromium, atau Brave."
        )

    opsi = Options()
    biner = cari_biner(konf)
    if biner:
        opsi.binary_location = biner
    if konf.headless:
        opsi.add_argument("--headless=new")
    if ambil_benar("NO_SANDBOX", False):
        opsi.add_argument("--no-sandbox")
    opsi.add_argument("--no-first-run")
    opsi.add_argument("--no-default-browser-check")
    opsi.add_argument("--disable-dev-shm-usage")
    opsi.add_argument("--window-size=1366,768")
    opsi.add_argument("--lang=id-ID")

    driver_biner = cari_driver(konf)
    layanan = Service(driver_biner) if driver_biner else Service()
    return webdriver.Chrome(service=layanan, options=opsi)


def tutup_driver(driver: webdriver.Chrome) -> None:
    try:
        driver.quit()
    except Exception:
        pass
