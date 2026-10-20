"""Test case halaman login: TC-LGN-01 dan TC-LGN-02."""

from __future__ import annotations

import pytest

from src.browser import buat_driver, tutup_driver
from src.halaman.login import HalamanLogin

# Pesan galat tidak boleh menyebut isian yang salah, hanya menyatakan login gagal.
KATA_ISIAN = ("password", "sandi", "username", "nama pengguna", "akun tidak")


@pytest.fixture(scope="module")
def browser_login(konfigurasi):
    """Browser tersendiri supaya uji login tidak mengganggu sesi uji lain."""
    driver = buat_driver(konfigurasi)
    yield driver
    tutup_driver(driver)


def _siap_login(driver, konfigurasi):
    halaman = HalamanLogin(driver, konfigurasi).buka()
    return halaman


@pytest.mark.lgn
def test_tc_lgn_01_login_kredensial_valid(browser_login, konfigurasi):
    """TC-LGN-01: kredensial valid harus masuk ke dasbor mahasiswa."""
    if not konfigurasi.punya_kredensial:
        pytest.skip("Kredensial akun mahasiswa belum diisi (SUNAN_PENGGUNA dan SUNAN_SANDI).")

    halaman = _siap_login(browser_login, konfigurasi)
    halaman.isi_kredensial(konfigurasi.pengguna, konfigurasi.sandi)
    if not halaman.tunggu_captcha():
        pytest.skip("reCAPTCHA belum diisi. Jalankan ulang dengan --headed lalu lengkapi CAPTCHA.")
    halaman.kirim()

    hasil = halaman.cek_hasil()
    assert hasil.berhasil, f"Login seharusnya berhasil: {hasil.pesan or hasil.alasan}"


@pytest.mark.lgn
def test_tc_lgn_02_login_kredensial_tidak_valid(browser_login, konfigurasi):
    """TC-LGN-02: password salah harus ditolak tanpa menyebut isian yang salah."""
    if not konfigurasi.punya_kredensial:
        pytest.skip("Kredensial akun mahasiswa belum diisi (SUNAN_PENGGUNA dan SUNAN_SANDI).")

    halaman = _siap_login(browser_login, konfigurasi)
    halaman.isi_kredensial(konfigurasi.pengguna, "kata-sandi-salah-untuk-uji")
    if not halaman.tunggu_captcha():
        pytest.skip("reCAPTCHA belum diisi. Jalankan ulang dengan --headed lalu lengkapi CAPTCHA.")
    halaman.kirim()

    hasil = halaman.cek_hasil()
    assert not hasil.berhasil, "Login dengan password salah seharusnya ditolak"
    assert hasil.masih_di_login, "Pengguna seharusnya tetap berada di halaman login"
    assert hasil.pesan, "Pesan kesalahan login tidak ditemukan di halaman"

    pesan_rendah = hasil.pesan.lower()
    for kata in KATA_ISIAN:
        assert kata not in pesan_rendah, f"Pesan galat menyebut isian yang salah: {hasil.pesan}"
