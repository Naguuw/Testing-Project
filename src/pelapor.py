# Pencatatan hasil uji: log, tangkapan layar, dan laporan akhir.
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


def siapkan_log(
    folder: Path, nama_berkas: str = "pengujian.log", ke_konsol: bool = True
) -> logging.Logger:
    folder.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("uji")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    format_log = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    if ke_konsol:
        konsol = logging.StreamHandler()
        konsol.setFormatter(format_log)
        logger.addHandler(konsol)
    berkas = logging.FileHandler(folder / nama_berkas, encoding="utf-8")
    berkas.setFormatter(format_log)
    logger.addHandler(berkas)
    return logger


def baca_hasil(junit: Path) -> dict[str, int]:
    # Menghitung jumlah lulus, gagal, dan dilewati dari JUnit XML.
    jumlah = {"lulus": 0, "gagal": 0, "dilewati": 0}
    if not junit.exists():
        return jumlah
    pohon = ET.parse(junit).getroot()
    for tes in pohon.iter("testcase"):
        if tes.find("skipped") is not None:
            jumlah["dilewati"] += 1
        elif tes.find("failure") is not None or tes.find("error") is not None:
            jumlah["gagal"] += 1
        else:
            jumlah["lulus"] += 1
    return jumlah


def simpan_tangkapan(driver, folder: Path, nama: str) -> Path:
    # Dipakai sebagai bukti saat skenario gagal.
    folder.mkdir(parents=True, exist_ok=True)
    stempel = datetime.now().strftime("%Y%m%d-%H%M%S")
    berkas = folder / f"{nama}_{stempel}.png"
    driver.save_screenshot(str(berkas))
    return berkas


def tulis_laporan(
    junit: Path, folder: Path, konfigurasi, nama_browser: str, biner: str | None
) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    tujuan = folder / f"laporan_{nama_browser}.txt"

    baris = [
        "LAPORAN PENGUJIAN OTOMATIS - SUNAN UMK",
        f"Waktu              : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        f"Situs              : {konfigurasi.url}",
        f"Browser            : {nama_browser} (headless={konfigurasi.headless})",
        f"Lokasi browser     : {biner or 'ditemukan otomatis oleh Selenium Manager'}",
        f"Batas ukuran uji   : {konfigurasi.batas_unggah_mb} MB",
        "",
    ]

    jumlah = baca_hasil(junit)
    if junit.exists():
        pohon = ET.parse(junit).getroot()
        for tes in pohon.iter("testcase"):
            nama = tes.get("name", "")
            salah = tes.find("failure") if tes.find("failure") is not None else tes.find("error")
            dilewati = tes.find("skipped")
            if dilewati is not None:
                status = "dilewati"
                alasan = dilewati.get("message", "") or ""
            elif salah is not None:
                status = "gagal"
                alasan = (salah.get("message", "") or "").strip().splitlines()[:1]
                alasan = alasan[0] if alasan else ""
            else:
                status = "lulus"
                alasan = ""
            baris.append(f"[{status.upper():<8}] {nama}")
            if alasan:
                baris.append(f"           {alasan}")
    total = sum(jumlah.values())
    baris += [
        "",
        f"RINGKASAN: {jumlah['lulus']} lulus, {jumlah['gagal']} gagal, "
        f"{jumlah['dilewati']} dilewati dari {total} test case",
        "Test case yang dilewati berarti skenario terhalang "
        "(misalnya CAPTCHA atau kredensial belum diisi).",
    ]
    tujuan.write_text("\n".join(baris) + "\n", encoding="utf-8")
    return tujuan
