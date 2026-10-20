"""Fixture bersama: konfigurasi, berkas uji, browser, dan sesi mahasiswa."""

from __future__ import annotations

import logging

import pytest

from src.browser import buat_driver, tutup_driver
from src.data_uji import siapkan_berkas
from src.halaman.login import HalamanLogin
from src.konfigurasi import bangun_konfigurasi


@pytest.fixture(scope="session")
def konfigurasi():
    return bangun_konfigurasi()


@pytest.fixture(scope="session")
def berkas(konfigurasi):
    return siapkan_berkas(konfigurasi.folder_berkas, konfigurasi.batas_unggah_mb)


@pytest.fixture(scope="session")
def browser(konfigurasi):
    """Browser khusus skenario unggah berkas; dipakai sekali se-sesi."""
    driver = buat_driver(konfigurasi)
    yield driver
    tutup_driver(driver)


@pytest.fixture(scope="session")
def sesi_mahasiswa(browser, konfigurasi):
    """Masuk ke Sunan UMK sekali lalu pakai sesi itu untuk seluruh uji unggah."""
    log = logging.getLogger("uji")
    if not konfigurasi.punya_kredensial:
        pytest.skip("Kredensial akun mahasiswa belum diisi (SUNAN_PENGGUNA dan SUNAN_SANDI).")

    halaman = HalamanLogin(browser, konfigurasi).buka()
    halaman.isi_kredensial(konfigurasi.pengguna, konfigurasi.sandi)
    if not halaman.tunggu_captcha():
        pytest.skip("reCAPTCHA belum diisi. Jalankan ulang dengan --headed lalu lengkapi CAPTCHA.")
    halaman.kirim()
    hasil = halaman.cek_hasil()
    if not hasil.berhasil:
        pytest.skip(f"Login gagal, skenario tidak bisa dijalankan: {hasil.pesan or hasil.alasan}")
    log.info("Sesi mahasiswa siap dipakai untuk uji unggah berkas.")
    return hasil
