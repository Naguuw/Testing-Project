# Konfigurasi uji: dibaca dari berkas .env lalu dipakai seluruh modul.
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent

BROWSER_DIDUKUNG = ("chrome", "firefox", "edge")
ALIAS_BROWSER = {"chromium": "chrome", "brave": "chrome", "msedge": "edge", "mozilla": "firefox"}


@dataclass(frozen=True)
class Konfigurasi:
    url: str
    pengguna: str
    sandi: str
    browser: tuple[str, ...]
    headless: bool
    biner: dict[str, str]
    driver: dict[str, str]
    url_tugas: str
    folder_berkas: Path
    folder_hasil: Path
    waktu_tunggu: int
    waktu_captcha: int
    waktu_login_manual: int
    waktu_upload: int
    batas_upload_mb: int

    @property
    def punya_kredensial(self) -> bool:
        return bool(self.pengguna and self.sandi)


def muat_env(path: Path | None = None) -> None:
    # Nilai yang sudah ada di environment tidak ditimpa.
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


def daftar_browser(nilai: str) -> tuple[str, ...]:
    # Alias seperti brave atau chromium dipetakan ke nama baku.
    hasil: list[str] = []
    for bagian in nilai.split(","):
        nama = bagian.strip().lower()
        if not nama:
            continue
        nama = ALIAS_BROWSER.get(nama, nama)
        if nama not in BROWSER_DIDUKUNG:
            raise ValueError(
                f"Browser '{nama}' tidak didukung. Pilihan: {', '.join(BROWSER_DIDUKUNG)}."
            )
        if nama not in hasil:
            hasil.append(nama)
    return tuple(hasil) or ("chrome",)


def browser_terpilih() -> tuple[str, ...]:
    muat_env()
    return daftar_browser(os.environ.get("BROWSER_UJI", "chrome"))


def bangun_konfigurasi() -> Konfigurasi:
    muat_env()
    return Konfigurasi(
        url=ambil_teks("SUNAN_URL", "https://sunan.umk.ac.id"),
        pengguna=ambil_teks("SUNAN_PENGGUNA"),
        sandi=ambil_teks("SUNAN_SANDI"),
        browser=daftar_browser(os.environ.get("BROWSER_UJI", "chrome")),
        headless=ambil_benar("HEADLESS", True),
        biner={
            "chrome": ambil_teks("BINER_CHROME"),
            "firefox": ambil_teks("BINER_FIREFOX"),
            "edge": ambil_teks("BINER_EDGE"),
        },
        driver={
            "chrome": ambil_teks("DRIVER_CHROME"),
            "firefox": ambil_teks("DRIVER_FIREFOX"),
            "edge": ambil_teks("DRIVER_EDGE"),
        },
        url_tugas=ambil_teks("SUNAN_URL_TUGAS"),
        folder_berkas=AKAR / "berkas",
        folder_hasil=AKAR / "hasil",
        waktu_tunggu=ambil_angka("WAKTU_TUNGGU", 30),
        waktu_captcha=ambil_angka("WAKTU_CAPTCHA", 120),
        waktu_login_manual=ambil_angka("WAKTU_LOGIN_MANUAL", 300),
        waktu_upload=ambil_angka("WAKTU_UPLOAD", 90),
        batas_upload_mb=ambil_angka("BATAS_UPLOAD_MB", 5),
    )
