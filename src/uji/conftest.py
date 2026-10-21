# Fixture bersama: Konfigurasi, berkas uji, browser, dan sesi mahasiswa.
from __future__ import annotations

import logging

import pytest

from src.browser import buat_driver, tutup_driver
from src.browser import profil_browser as buat_profil
from src.data_uji import siapkan_berkas
from src.halaman.login import HalamanLogin
from src.konfigurasi import ambil_benar, bangun_konfigurasi, browser_terpilih
from src.pelapor import siapkan_log, simpan_bukti

BROWSER_UJI = browser_terpilih()


@pytest.fixture(scope="session", autouse=True)
def log_uji(konfigurasi, profil_browser):
    # Log skenario dipisah per browser.
    return siapkan_log(konfigurasi.folder_hasil, f"pengujian_{profil_browser.nama}.log")


@pytest.fixture(scope="session")
def konfigurasi():
    return bangun_konfigurasi()


@pytest.fixture(scope="session")
def berkas(konfigurasi):
    return siapkan_berkas(konfigurasi.folder_berkas, konfigurasi.batas_upload_mb)


@pytest.fixture(scope="session", params=BROWSER_UJI, ids=lambda nama: nama)
def profil_browser(request, konfigurasi):
    # Fixture diparameterisasi agar skenario diulang di tiap browser.
    return buat_profil(request.param, konfigurasi)


@pytest.fixture(scope="session")
def browser(konfigurasi, profil_browser):
    # Satu browser dipakai bersama seluruh skenario, jadi captcha cukup dicentang sekali.
    driver = buat_driver(konfigurasi, profil_browser)
    yield driver
    tutup_driver(driver)


@pytest.fixture(scope="session")
def berkas_sesi(konfigurasi, profil_browser):
    # Sesi login disimpan per browser supaya skenario berikutnya tidak perlu captcha.
    return konfigurasi.folder_hasil / f"sesi_{profil_browser.nama}.json"


@pytest.fixture(scope="session")
def sesi_mahasiswa(browser, konfigurasi, berkas_sesi):
    # Login cukup sekali untuk semua skenario upload.
    log = logging.getLogger("uji")
    halaman = HalamanLogin(browser, konfigurasi)

    if ambil_benar("LOGIN_MANUAL", False):
        halaman.buka()
        if not halaman.tunggu_login_manual():
            pytest.skip("Login manual tidak selesai dalam batas waktu.")
        halaman.simpan_sesi(berkas_sesi)
        return None

    if not konfigurasi.punya_kredensial:
        pytest.skip("Kredensial akun mahasiswa belum diisi (SUNAN_PENGGUNA dan SUNAN_SANDI).")

    if halaman.sudah_masuk():
        # Sesi dari test case login sebelumnya masih hidup, dipakai lagi.
        return None

    if halaman.pulihkan_sesi(berkas_sesi) and halaman.sudah_masuk():
        log.info("Sesi login dipakai ulang, captcha tidak perlu dicentang lagi.")
        return None

    halaman.buka()
    hasil = halaman.coba_login(konfigurasi.pengguna, konfigurasi.sandi)
    if not hasil.berhasil:
        pytest.skip(f"Login gagal, skenario tidak bisa dijalankan: {hasil.pesan or hasil.alasan}")
    halaman.simpan_sesi(berkas_sesi)
    log.info("Sesi mahasiswa siap dipakai untuk uji upload berkas.")
    return hasil


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # Bukti diambil tepat saat test gagal, sebelum keadaan browser berubah.
    hasil = yield
    laporan = hasil.get_result()
    setattr(item, "laporan_uji", laporan)
    if not laporan.failed:
        return
    try:
        driver = item._request.getfixturevalue("browser")
        konfigurasi = item._request.getfixturevalue("konfigurasi")
    except Exception:
        return
    for berkas in simpan_bukti(driver, konfigurasi.folder_hasil / "bukti", item.name):
        logging.getLogger("uji").warning("Bukti kegagalan: %s", berkas)
