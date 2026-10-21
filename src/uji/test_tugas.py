# Test case pengumpulan tugas: TC-TGS-01, TC-TGS-02, TC-TGS-03, dan TC-TGS-05.
from __future__ import annotations

import pytest

from src.halaman.tugas import HalamanTugas


@pytest.fixture(scope="module")
def halaman_tugas(browser, konfigurasi, sesi_mahasiswa):
    return HalamanTugas(browser, konfigurasi)


@pytest.mark.tgs
def test_tc_tgs_01_upload_pdf_valid(halaman_tugas, berkas):
    # TC-TGS-01: PDF valid diterima dan terlampir di area Files.
    halaman_tugas.buka()
    hasil = halaman_tugas.upload(berkas["pdf_valid"])
    assert hasil.diterima, f"PDF valid seharusnya diterima: {hasil.pesan}"
    assert hasil.nama_terupload, "Nama berkas tidak tampil di area Files"


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
