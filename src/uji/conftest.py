# Fixture bersama: konfigurasi, berkas uji, browser, dan sesi mahasiswa.

from __future__ import annotations

import logging
import os

import pytest

from src.browser import buat_driver, tutup_driver
from src.browser import profil_browser as buat_profil
from src.data_uji import siapkan_berkas
from src.halaman.login import HalamanLogin
from src.konfigurasi import ambil_benar, bangun_konfigurasi, browser_terpilih
from src.pelapor import siapkan_log

BROWSER_UJI = browser_terpilih()


@pytest.fixture(scope="session", autouse=True)
def log_uji(konfigurasi):
    # Log skenario dipisah per browser.
    return siapkan_log(
        konfigurasi.folder_hasil, f"pengujian_{os.environ.get('BROWSER_UJI', 'chrome')}.log"
    )


@pytest.fixture(scope="session")
def konfigurasi():
    return bangun_konfigurasi()


@pytest.fixture(scope="session")
def berkas(konfigurasi):
    return siapkan_berkas(konfigurasi.folder_berkas, konfigurasi.batas_unggah_mb)


@pytest.fixture(scope="session", params=BROWSER_UJI, ids=lambda nama: nama)
def profil_browser(request, konfigurasi):
    # Fixture diparameterisasi agar skenario diulang di tiap browser.
    return buat_profil(request.param, konfigurasi)


@pytest.fixture(scope="session")
def browser(konfigurasi, profil_browser):
    # Satu browser dipakai bersama seluruh skenario unggah.
    driver = buat_driver(konfigurasi, profil_browser)
    yield driver
    tutup_driver(driver)


@pytest.fixture(scope="module")
def browser_login(konfigurasi, profil_browser):
    # Browser terpisah supaya uji login tidak mengganggu sesi uji lain.
    driver = buat_driver(konfigurasi, profil_browser)
    yield driver
    tutup_driver(driver)


@pytest.fixture(scope="session")
def sesi_mahasiswa(browser, konfigurasi):
    # Login cukup sekali untuk semua skenario unggah.
    log = logging.getLogger("uji")
    manual = ambil_benar("LOGIN_MANUAL", False)

    halaman = HalamanLogin(browser, konfigurasi).buka()
    if manual:
        if not halaman.tunggu_login_manual():
            pytest.skip("Login manual tidak selesai dalam batas waktu.")
        return None

    if not konfigurasi.punya_kredensial:
        pytest.skip("Kredensial akun mahasiswa belum diisi (SUNAN_PENGGUNA dan SUNAN_SANDI).")

    halaman.isi_kredensial(konfigurasi.pengguna, konfigurasi.sandi)
    if not halaman.tunggu_captcha():
        pytest.skip("reCAPTCHA belum diisi. Jalankan ulang dengan --headed lalu lengkapi CAPTCHA.")
    halaman.kirim()
    hasil = halaman.cek_hasil()
    if not hasil.berhasil:
        pytest.skip(f"Login gagal, skenario tidak bisa dijalankan: {hasil.pesan or hasil.alasan}")
    log.info("Sesi mahasiswa siap dipakai untuk uji unggah berkas.")
    return hasil
