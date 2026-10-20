"""Pencatatan hasil uji: log, tangkapan layar, dan laporan akhir."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


def siapkan_log(folder: Path) -> logging.Logger:
    folder.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("uji")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    format_log = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    konsol = logging.StreamHandler()
    konsol.setFormatter(format_log)
    berkas = logging.FileHandler(folder / "pengujian.log", encoding="utf-8")
    berkas.setFormatter(format_log)
    logger.addHandler(konsol)
    logger.addHandler(berkas)
    return logger


def simpan_tangkapan(driver, folder: Path, nama: str) -> Path:
    """Simpan screenshot sebagai bukti saat sebuah skenario gagal."""
    folder.mkdir(parents=True, exist_ok=True)
    stempel = datetime.now().strftime("%Y%m%d-%H%M%S")
    berkas = folder / f"{nama}_{stempel}.png"
    driver.save_screenshot(str(berkas))
    return berkas


def tulis_laporan(junit: Path, folder: Path, konfigurasi) -> Path:
    """Ubah hasil pytest (JUnit XML) menjadi laporan teks yang mudah dibaca."""
    folder.mkdir(parents=True, exist_ok=True)
    tujuan = folder / "laporan_pengujian.txt"

    baris = [
        "LAPORAN PENGUJIAN OTOMATIS - SUNAN UMK",
        f"Waktu              : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        f"Situs              : {konfigurasi.url}",
        f"Peramban           : {konfigurasi.peramban} (headless={konfigurasi.headless})",
        f"Batas ukuran uji   : {konfigurasi.batas_unggah_mb} MB",
        "",
    ]

    jumlah = {"lulus": 0, "gagal": 0, "dilewati": 0}
    if junit.exists():
        pohon = ET.parse(junit).getroot()
        for tes in pohon.iter("testcase"):
            nama = tes.get("name", "")
            salah = tes.find("failure") if tes.find("failure") is not None else tes.find("error")
            dilewati = tes.find("skipped")
            if dilewati is not None:
                status = "dilewati"
                jumlah["dilewati"] += 1
                alasan = dilewati.get("message", "") or ""
            elif salah is not None:
                status = "gagal"
                jumlah["gagal"] += 1
                alasan = (salah.get("message", "") or "").strip().splitlines()[:1]
                alasan = alasan[0] if alasan else ""
            else:
                status = "lulus"
                jumlah["lulus"] += 1
                alasan = ""
            baris.append(f"[{status.upper():<8}] {nama}")
            if alasan:
                baris.append(f"           {alasan}")

    total = sum(jumlah.values())
    baris += [
        "",
        f"RINGKASAN: {jumlah['lulus']} lulus, {jumlah['gagal']} gagal, "
        f"{jumlah['dilewati']} dilewati dari {total} test case",
        "Test case yang dilewati berarti skenario terhalang (misalnya CAPTCHA atau kredensial belum diisi).",
    ]
    tujuan.write_text("\n".join(baris) + "\n", encoding="utf-8")
    return tujuan
