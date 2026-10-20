"""Fixture bersama: konfigurasi, berkas uji, browser, dan sesi mahasiswa."""

from __future__ import annotations

import logging

import pytest

from src.browser import buat_driver, tutup_driver
from src.browser import profil_browser as buat_profil
from src.data_uji import siapkan_berkas
from src.halaman.login import HalamanLogin
from src.konfigurasi import bangun_konfigurasi, browser_terpilih

BROWSER_UJI = browser_terpilih()


@pytest.fixture(scope="session")
def konfigurasi():
    return bangun_konfigurasi()


@pytest.fixture(scope="session")
def berkas(konfigurasi):
    return siapkan_berkas(konfigurasi.folder_berkas, konfigurasi.batas_unggah_mb)


@pytest.fixture(scope="session", params=BROWSER_UJI, ids=lambda nama: nama)
def profil_browser(request, konfigurasi):
    """Satu profil per browser yang diuji; dipakai untuk mengulang skenario di tiap browser."""
    return buat_profil(request.param, konfigurasi)


@pytest.fixture(scope="session")
def browser(konfigurasi, profil_browser):
    """Browser khusus skenario unggah berkas; dipakai sekali se-sesi."""
    driver = buat_driver(konfigurasi, profil_browser)
    yield driver
    tutup_driver(driver)


@pytest.fixture(scope="module")
def browser_login(konfigurasi, profil_browser):
    """Browser tersendiri supaya uji login tidak mengganggu sesi uji lain."""
    driver = buat_driver(konfigurasi, profil_browser)
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
