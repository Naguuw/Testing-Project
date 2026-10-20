"""Titik eksekusi pengujian otomatis website e-learning Sunan UMK.

Jalankan:
    python main.py                 semua test case otomatis
    python main.py --headed        tampilkan browser (perlu bila ada CAPTCHA)
    python main.py --pilih TC-LGN-01,TC-TGS-01
    python main.py --panduan       tampilkan skenario uji manual
    python main.py --daftar        tampilkan daftar test case
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent
if str(AKAR) not in sys.path:
    sys.path.insert(0, str(AKAR))

import pytest

from src.data_uji import siapkan_berkas
from src.konfigurasi import bangun_konfigurasi
from src.pelapor import siapkan_log, tulis_laporan
from src.uji.panduan_manual import cetak_panduan, skenario_manual

DAFTAR_TEST_CASE = [
    ("TC-LGN-01", "Login dengan kredensial valid", "otomatis"),
    ("TC-LGN-02", "Login dengan kredensial tidak valid", "otomatis"),
    ("TC-MKL-01", "Membuka mata kuliah dan mengunduh materi", "manual"),
    ("TC-TGS-01", "Unggah tugas format PDF valid", "otomatis"),
    ("TC-TGS-02", "Ukuran di bawah dan tepat pada batas", "otomatis"),
    ("TC-TGS-03", "Berkas kosong (0 byte)", "otomatis"),
    ("TC-TGS-04", "Koneksi terputus saat unggah", "manual"),
    ("TC-TGS-05", "Format tidak diizinkan", "otomatis"),
    ("TC-TGS-06", "Mengirim dua berkas dengan nama yang sama", "manual"),
    ("TC-AKS-01", "Mahasiswa membuka halaman penilaian", "manual"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pengujian otomatis website e-learning Sunan UMK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--pilih", help="ID test case yang dijalankan, misal TC-LGN-01,TC-TGS-01")
    parser.add_argument("--headed", action="store_true", help="Tampilkan browser (dibutuhkan bila ada CAPTCHA)")
    parser.add_argument("--daftar", action="store_true", help="Tampilkan daftar test case")
    parser.add_argument("--panduan", action="store_true", help="Tampilkan skenario uji manual")
    parser.add_argument("--buat-berkas", action="store_true", help="Siapkan berkas uji lalu berhenti")
    parser.add_argument("--url", help="Alamat situs yang diuji")
    parser.add_argument("--pengguna", help="Nama pengguna akun uji")
    parser.add_argument("--sandi", help="Kata sandi akun uji")
    parser.add_argument("--url-tugas", help="Alamat halaman tugas yang dipakai uji unggah")
    return parser.parse_args()


def terapkan_override(args: argparse.Namespace) -> None:
    """Nilai dari baris perintah lebih tinggi prioritasnya daripada berkas .env."""
    pasangan = {
        "SUNAN_URL": args.url,
        "SUNAN_PENGGUNA": args.pengguna,
        "SUNAN_SANDI": args.sandi,
        "SUNAN_URL_TUGAS": args.url_tugas,
    }
    for kunci, nilai in pasangan.items():
        if nilai:
            os.environ[kunci] = nilai
    if args.headed:
        os.environ["HEADLESS"] = "0"


def kunci_pilihan(daftar_id: str) -> str:
    """Ubah daftar ID test case menjadi penapis pytest (-k)."""
    kunci = []
    for id_uji in daftar_id.split(","):
        id_uji = id_uji.strip().lower()
        if id_uji:
            kunci.append(id_uji.replace("-", "_"))
    return " or ".join(kunci)


def pisahkan_pilihan(daftar_id: str) -> tuple[list[str], list[str]]:
    """Pisahkan ID pilihan menjadi yang dikerjakan otomatis dan yang manual."""
    otomatis, manual = [], []
    for id_uji in (bagian.strip().upper() for bagian in daftar_id.split(",")):
        if not id_uji:
            continue
        cara = dict((kode, metode) for kode, _, metode in DAFTAR_TEST_CASE).get(id_uji)
        if cara == "manual":
            manual.append(id_uji)
        else:
            otomatis.append(id_uji)
    return otomatis, manual


def cetak_daftar() -> None:
    print()
    print("DAFTAR TEST CASE")
    print("=" * 72)
    for id_uji, skenario, cara in DAFTAR_TEST_CASE:
        print(f"{id_uji} | {cara:<7} | {skenario}")
    print("=" * 72)


def main() -> int:
    args = parse_args()

    if args.daftar:
        cetak_daftar()
        return 0
    if args.panduan:
        cetak_panduan()
        return 0

    terapkan_override(args)
    os.chdir(AKAR)

    konfigurasi = bangun_konfigurasi()
    logger = siapkan_log(konfigurasi.folder_hasil)
    siapkan_berkas(konfigurasi.folder_berkas, konfigurasi.batas_unggah_mb)

    if args.buat_berkas:
        logger.info("Berkas uji siap di %s", konfigurasi.folder_berkas)
        return 0

    if not konfigurasi.punya_kredensial:
        logger.warning(
            "Kredensial akun mahasiswa belum diisi, seluruh skenario akan dilewati. "
            "Isi SUNAN_PENGGUNA dan SUNAN_SANDI di berkas .env."
        )
    if not konfigurasi.url_tugas:
        logger.warning("SUNAN_URL_TUGAS belum diisi, uji unggah berkas tidak dapat dijalankan.")

    otomatis, manual = ([], [])
    if args.pilih:
        otomatis, manual = pisahkan_pilihan(args.pilih)
        if manual:
            skenario_manual(manual)
        if not otomatis:
            return 0

    logger.info("Menguji %s", konfigurasi.url)
    junit = konfigurasi.folder_hasil / "junit.xml"
    argumen = ["src/uji", "-ra", f"--junitxml={junit}"]
    if otomatis:
        argumen += ["-k", kunci_pilihan(",".join(otomatis))]

    kode = pytest.main(argumen)
    laporan = tulis_laporan(junit, konfigurasi.folder_hasil, konfigurasi)

    print()
    print(laporan.read_text(encoding="utf-8"))
    print(f"Laporan tersimpan di {laporan}")
    return int(kode)


if __name__ == "__main__":
    sys.exit(main())
