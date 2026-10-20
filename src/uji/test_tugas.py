# Test case pengumpulan tugas: TC-TGS-01, TC-TGS-02, TC-TGS-03, dan TC-TGS-05.

from __future__ import annotations

import pytest

from src.halaman.tugas import HalamanTugas


@pytest.fixture(scope="module")
def halaman_tugas(browser, konfigurasi, sesi_mahasiswa):
    return HalamanTugas(browser, konfigurasi)


@pytest.mark.tgs
def test_tc_tgs_01_unggah_pdf_valid(halaman_tugas, berkas):
    # TC-TGS-01: PDF valid diterima dan statusnya menjadi terkumpul.
    halaman_tugas.buka()
    nama = halaman_tugas.unggah(berkas["pdf_valid"])
    halaman_tugas.kirim()

    pesan = halaman_tugas.pesan_tolak()
    assert not pesan, f"PDF valid seharusnya diterima, tetapi muncul pesan: {pesan}"

    terkumpul = halaman_tugas.sudah_terkumpul() or nama in halaman_tugas.nama_berkas_terunggah()
    assert terkumpul, "Status pengumpulan belum menunjukkan berkas terkumpul"


@pytest.mark.tgs
def test_tc_tgs_02_ukuran_batas(halaman_tugas, berkas, konfigurasi):
    # TC-TGS-02: berkas di bawah dan tepat pada batas ukuran diterima.
    for kunci in ("pdf_batas_bawah", "pdf_batas_tepat"):
        berkas_uji = berkas[kunci]
        ukuran = berkas_uji.stat().st_size
        halaman_tugas.buka()
        halaman_tugas.unggah(berkas_uji)
        halaman_tugas.kirim()

        pesan = halaman_tugas.pesan_tolak()
        assert not pesan, f"Berkas {ukuran} byte ditolak: {pesan}"


@pytest.mark.tgs
def test_tc_tgs_03_berkas_kosong(halaman_tugas, berkas):
    # TC-TGS-03: berkas 0 byte ditolak dan status pengumpulan tidak berubah.
    halaman_tugas.buka()
    halaman_tugas.unggah(berkas["berkas_kosong"])
    halaman_tugas.kirim()

    pesan = halaman_tugas.pesan_tolak()
    assert pesan, "Berkas kosong seharusnya ditolak dengan pesan yang jelas"
    assert (
        not halaman_tugas.sudah_terkumpul()
    ), "Status pengumpulan berubah setelah berkas kosong diunggah"


@pytest.mark.tgs
def test_tc_tgs_05_format_tidak_diizinkan(halaman_tugas, berkas):
    # TC-TGS-05: berkas .exe ditolak dengan pesan format tidak didukung.
    halaman_tugas.buka()
    halaman_tugas.unggah(berkas["berkas_terlarang"])
    halaman_tugas.kirim()

    pesan = halaman_tugas.pesan_tolak()
    assert pesan, "Berkas .exe seharusnya ditolak dengan pesan yang jelas"
    assert (
        not halaman_tugas.sudah_terkumpul()
    ), "Status pengumpulan berubah setelah berkas terlarang diunggah"
