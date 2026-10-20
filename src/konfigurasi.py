"""Konfigurasi uji: dibaca dari berkas .env lalu dipakai seluruh modul."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Konfigurasi:
    url: str
    pengguna: str
    sandi: str
    peramban: str
    headless: bool
    biner_peramban: str
    driver_biner: str
    url_tugas: str
    folder_berkas: Path
    folder_hasil: Path
    waktu_tunggu: int
    waktu_captcha: int
    batas_unggah_mb: int

    @property
    def punya_kredensial(self) -> bool:
        return bool(self.pengguna and self.sandi)


def muat_env(path: Path | None = None) -> None:
    """Isi os.environ dari berkas .env tanpa menimpa nilai yang sudah ada."""
    berkas = path or AKAR / ".env"
    if not berkas.exists():
        return
    for baris in berkas.read_text(encoding="utf-8").splitlines():
        baris = baris.strip()
        if not baris or baris.startswith("#") or "=" not in baris:
            continue
        kunci, nilai = baris.split("=", 1)
        os.environ.setdefault(kunci.strip(), nilai.strip().strip('"').strip("'"))


def ambil_teks(nama: str, bawaan: str = "") -> str:
    return os.environ.get(nama, bawaan).strip()


def ambil_angka(nama: str, bawaan: int) -> int:
    try:
        return int(os.environ.get(nama, bawaan))
    except ValueError:
        return bawaan


def ambil_benar(nama: str, bawaan: bool) -> bool:
    nilai = os.environ.get(nama)
    if nilai is None:
        return bawaan
    return nilai.strip().lower() in {"1", "true", "ya", "on"}


def bangun_konfigurasi() -> Konfigurasi:
    muat_env()
    return Konfigurasi(
        url=ambil_teks("SUNAN_URL", "https://sunan.umk.ac.id"),
        pengguna=ambil_teks("SUNAN_PENGGUNA"),
        sandi=ambil_teks("SUNAN_SANDI"),
        peramban=ambil_teks("PERAMBAN", "chrome").lower(),
        headless=ambil_benar("HEADLESS", True),
        biner_peramban=ambil_teks("BROWSER_BINARY"),
        driver_biner=ambil_teks("CHROMEDRIVER_PATH"),
        url_tugas=ambil_teks("SUNAN_URL_TUGAS"),
        folder_berkas=AKAR / "berkas",
        folder_hasil=AKAR / "hasil",
        waktu_tunggu=ambil_angka("WAKTU_TUNGGU", 15),
        waktu_captcha=ambil_angka("WAKTU_CAPTCHA", 120),
        batas_unggah_mb=ambil_angka("BATAS_UNGGAH_MB", 5),
    )
