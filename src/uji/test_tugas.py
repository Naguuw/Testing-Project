# Test case pengumpulan tugas: TC-TGS-01, TC-TGS-02, TC-TGS-03, dan TC-TGS-05.
from __future__ import annotations

from pathlib import Path

import pytest

from src.data_uji import daftar_berkas_upload
from src.halaman.tugas import HalamanTugas

# Aturan unggah yang berlaku di situs: ekstensi ini, maksimal 20 MB, dan tidak boleh kosong.
EKSTENSI_DITERIMA = (".doc", ".docx", ".pdf", ".rtf")
BATAS_UKURAN_SITUS = 20 * 1024 * 1024


@pytest.fixture(scope="module")
def halaman_tugas(browser, konfigurasi, sesi_mahasiswa):
    return HalamanTugas(browser, konfigurasi)


def _situs_menerima(berkas: Path) -> bool:
    # Harapan mengikuti aturan situs, bukan tebakan.
    ukuran = berkas.stat().st_size
    return berkas.suffix.lower() in EKSTENSI_DITERIMA and 0 < ukuran <= BATAS_UKURAN_SITUS


@pytest.mark.tgs
def test_tc_tgs_01_upload_berkas_di_folder(halaman_tugas, konfigurasi):
    # TC-TGS-01: setiap berkas di folder berkas diunggah, lalu hasilnya
    # dibandingkan dengan aturan unggah yang berlaku di situs.
    daftar = daftar_berkas_upload(konfigurasi.folder_berkas)
    if not daftar:
        pytest.skip("Folder berkas kosong, tidak ada berkas untuk diuji.")

    for berkas in daftar:
        halaman_tugas.buka()
        hasil = halaman_tugas.upload(berkas)
        if _situs_menerima(berkas):
            assert hasil.diterima, f"{berkas.name} seharusnya diterima: {hasil.pesan}"
            assert hasil.nama_terupload, f"Nama {berkas.name} tidak tampil di area Files"
        else:
            assert not hasil.diterima, f"{berkas.name} seharusnya ditolak, tapi diterima"
            assert hasil.pesan, f"{berkas.name} ditolak tanpa pesan yang jelas"


@pytest.mark.tgs
def test_tc_tgs_02_ukuran_batas(halaman_tugas, berkas, konfigurasi):
    # TC-TGS-02: berkas di bawah dan tepat pada batas ukuran diterima.
    for kunci in ("pdf_batas_bawah", "pdf_batas_tepat"):
        berkas_uji = berkas[kunci]
        ukuran = berkas_uji.stat().st_size
        halaman_tugas.buka()
        hasil = halaman_tugas.upload(berkas_uji)
        assert hasil.diterima, f"Berkas {ukuran} byte ditolak: {hasil.pesan}"
        assert hasil.nama_terupload, f"Nama berkas {ukuran} byte tidak tampil di area Files"


@pytest.mark.tgs
def test_tc_tgs_03_berkas_kosong(halaman_tugas, berkas):
    # TC-TGS-03: berkas 0 byte ditolak dengan pesan yang jelas.
    halaman_tugas.buka()
    hasil = halaman_tugas.upload(berkas["berkas_kosong"])
    assert not hasil.diterima, "Berkas kosong seharusnya ditolak"
    assert hasil.pesan, "Penolakan berkas kosong harus punya pesan yang jelas"


@pytest.mark.tgs
def test_tc_tgs_05_format_tidak_diizinkan(halaman_tugas, berkas):
    # TC-TGS-05: berkas .exe ditolak dengan pesan format tidak didukung.
    halaman_tugas.buka()
    hasil = halaman_tugas.upload(berkas["berkas_terlarang"])
    assert not hasil.diterima, "Berkas .exe seharusnya ditolak"
    assert hasil.pesan, "Penolakan berkas .exe harus punya pesan yang jelas"
