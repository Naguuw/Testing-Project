# Test case halaman login: TC-LGN-01 dan TC-LGN-02.
from __future__ import annotations

import pytest

from src.halaman.login import HalamanLogin
from src.konfigurasi import ambil_benar

# Pesan error tidak boleh menyebut isian yang salah, hanya menyatakan login gagal.
KATA_ISIAN = ("password", "sandi", "username", "nama pengguna", "akun tidak")


def _lewati_kalau_mode_manual() -> None:
    # Di mode login manual yang masuk adalah operator, jadi skenario login dilewati.
    if ambil_benar("LOGIN_MANUAL", False):
        pytest.skip("Mode login manual: skenario login dijalankan manual oleh operator.")


@pytest.mark.lgn
def test_tc_lgn_01_login_kredensial_valid(browser, konfigurasi, berkas_sesi):
    # TC-LGN-01: kredensial valid harus masuk ke dasbor mahasiswa.
    _lewati_kalau_mode_manual()
    if not konfigurasi.punya_kredensial:
        pytest.skip("Kredensial akun mahasiswa belum diisi (SUNAN_PENGGUNA dan SUNAN_SANDI).")

    halaman = HalamanLogin(browser, konfigurasi).buka()
    hasil = halaman.coba_login(konfigurasi.pengguna, konfigurasi.sandi)
    if hasil.terblokir:
        pytest.skip(f"Skenario terhalang: {hasil.alasan}")
    assert hasil.berhasil, f"Login seharusnya berhasil: {hasil.pesan or hasil.alasan}"
    # Sesi ini disimpan untuk skenario upload, jadi captcha tidak perlu dicentang dua kali.
    halaman.simpan_sesi(berkas_sesi)


@pytest.mark.lgn
def test_tc_lgn_02_login_kredensial_tidak_valid(browser, konfigurasi):
    # TC-LGN-02: password salah ditolak tanpa menyebut isian yang salah.
    _lewati_kalau_mode_manual()
    if not konfigurasi.punya_kredensial:
        pytest.skip("Kredensial akun mahasiswa belum diisi (SUNAN_PENGGUNA dan SUNAN_SANDI).")

    halaman = HalamanLogin(browser, konfigurasi).buka()
    hasil = halaman.coba_login(konfigurasi.pengguna, "kata-sandi-salah-untuk-uji")
    if hasil.terblokir:
        pytest.skip(f"Skenario terhalang: {hasil.alasan}")

    assert not hasil.berhasil, "Login dengan password salah seharusnya ditolak"
    assert hasil.masih_di_login, "Pengguna seharusnya tetap berada di halaman login"
    assert hasil.pesan, "Pesan kesalahan login tidak ditemukan di halaman"

    pesan_rendah = hasil.pesan.lower()
    for kata in KATA_ISIAN:
        assert kata not in pesan_rendah, f"Pesan error menyebut isian yang salah: {hasil.pesan}"
