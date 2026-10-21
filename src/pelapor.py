# Pencatatan hasil uji: log, bukti kegagalan, dan laporan akhir.

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


def _status_tes(tes: ET.Element) -> tuple[str, str]:
    # Status satu test case beserta alasannya, dibaca dari JUnit XML.
    dilewati = tes.find("skipped")
    if dilewati is not None:
        return "dilewati", dilewati.get("message", "") or ""
    salah = tes.find("failure") if tes.find("failure") is not None else tes.find("error")
    if salah is not None:
        pesan = (salah.get("message", "") or "").strip().splitlines()
        return "gagal", pesan[0] if pesan else ""
    return "lulus", ""


def baca_hasil(junit: Path) -> tuple[dict[str, int], list[tuple[str, str, str]]]:
    # Jumlah status per test case dan daftar rinciannya.
    jumlah = {"lulus": 0, "gagal": 0, "dilewati": 0}
    rincian: list[tuple[str, str, str]] = []
    if not junit.exists():
        return jumlah, rincian

    for tes in ET.parse(junit).getroot().iter("testcase"):
        status, alasan = _status_tes(tes)
        jumlah[status] += 1
        rincian.append((tes.get("name", ""), status, alasan))
    return jumlah, rincian


def tulis_laporan(
    junit: Path, folder: Path, konfigurasi, nama_browser: str, biner: str | None
) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    tujuan = folder / f"laporan_{nama_browser}.txt"
    jumlah, rincian = baca_hasil(junit)

    baris = [
        "LAPORAN PENGUJIAN OTOMATIS - SUNAN UMK",
        f"Waktu              : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        f"Situs              : {konfigurasi.url}",
        f"Browser            : {nama_browser} (headless={konfigurasi.headless})",
        f"Lokasi browser     : {biner or 'ditemukan otomatis oleh Selenium Manager'}",
        f"Batas ukuran uji   : {konfigurasi.batas_upload_mb} MB",
        "",
    ]
    for nama, status, alasan in rincian:
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


def simpan_bukti(driver, folder: Path, nama: str) -> list[Path]:
    # Bukti kegagalan: screenshot plus cuplikan DOM yang relevan.
    folder.mkdir(parents=True, exist_ok=True)
    bersih = "".join(
        character if character.isalnum() or character in "-_" else "_" for character in nama
    )
    berkas = []

    gambar = folder / f"{bersih}.png"
    try:
        driver.save_screenshot(str(gambar))
        berkas.append(gambar)
    except Exception:
        pass

    potongan = []
    for judul, selector in (
        ("area upload", ".fm-empty-container, .form-control-file, .filemanager"),
        ("modal file picker", ".file-picker"),
        ("daftar berkas", ".fnp-attachments, .filename, .file-name, .file-list"),
        ("status pengumpulan", ".submissionsection, .submission-info, .alert-info"),
    ):
        for elemen in driver.find_elements("css selector", selector):
            potongan.append(f"--- {judul} ---")
            potongan.append(elemen.get_attribute("outerHTML") or "")
            break

    potongan.append("--- file picker ---")
    for indeks, picker in enumerate(driver.find_elements("css selector", ".file-picker"), start=1):
        jumlah_berkas = driver.execute_script(
            'var input = arguments[0].querySelector("input[type=file]");'
            "return input ? input.files.length : -1;",
            picker,
        )
        potongan.append(
            f"  picker {indeks}: terlihat={picker.is_displayed()} "
            f"jumlah_berkas_terpilih={jumlah_berkas} "
            f"teks={(picker.text or '').strip()[:120]!r}"
        )

    potongan.append("--- filemanager ---")
    for elemen in driver.find_elements("css selector", ".filemanager"):
        potongan.append(f"  class={elemen.get_attribute('class')!r}")
        for medan in elemen.find_elements("css selector", "input[type=hidden]"):
            nilai = (medan.get_attribute("value") or "")[:80]
            potongan.append(f"  hidden name={medan.get_attribute('name')!r} value={nilai!r}")

    potongan.append("--- input, tombol, pesan ---")
    for elemen in driver.find_elements(
        "css selector", "input, button, [role='alert'], .alert, .invalid-feedback, .errormessage"
    ):
        potongan.append(
            f"  <{elemen.tag_name}> id={elemen.get_attribute('id')!r} "
            f"name={elemen.get_attribute('name')!r} type={elemen.get_attribute('type')!r} "
            f"class={elemen.get_attribute('class')!r} "
            f"teks={(elemen.text or '').strip()[:70]!r}"
        )

    berkas_dom = folder / f"{bersih}.html"
    berkas_dom.write_text("\n".join(potongan), encoding="utf-8")
    berkas.append(berkas_dom)
    return berkas
