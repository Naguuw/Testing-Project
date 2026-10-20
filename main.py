# Titik eksekusi pengujian otomatis website e-learning Sunan UMK.
#
# Perintah yang bisa dipakai:
# python main.py                 semua test case otomatis di semua browser
# python main.py --headed        tampilkan browser (perlu bila ada CAPTCHA)
# python main.py --login-manual  login sendiri di jendela browser
# python main.py --browser chrome,firefox
# python main.py --pilih TC-LGN-01,TC-TGS-01
# python main.py --panduan       tampilkan skenario uji manual
# python main.py --daftar        tampilkan daftar test case

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent
if str(AKAR) not in sys.path:
    sys.path.insert(0, str(AKAR))

from src.browser import cari_biner
from src.data_uji import siapkan_berkas
from src.konfigurasi import ambil_benar, bangun_konfigurasi
from src.pelapor import baca_hasil, siapkan_log, tulis_laporan
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
GARIS = "=" * 66


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pengujian otomatis website e-learning Sunan UMK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--pilih", help="ID test case yang dijalankan, misal TC-LGN-01,TC-TGS-01")
    parser.add_argument(
        "--browser", help="Browser yang diuji: chrome, firefox, edge (boleh dipisah koma)"
    )
    parser.add_argument(
        "--headed", action="store_true", help="Tampilkan browser (dibutuhkan bila ada CAPTCHA)"
    )
    parser.add_argument(
        "--login-manual",
        action="store_true",
        help="Login sendiri di jendela browser, lalu skenario lanjut otomatis",
    )
    parser.add_argument("--daftar", action="store_true", help="Tampilkan daftar test case")
    parser.add_argument("--panduan", action="store_true", help="Tampilkan skenario uji manual")
    parser.add_argument(
        "--buat-berkas", action="store_true", help="Siapkan berkas uji lalu berhenti"
    )
    parser.add_argument("--url", help="Alamat situs yang diuji")
    parser.add_argument("--pengguna", help="Nama pengguna akun uji")
    parser.add_argument("--sandi", help="Kata sandi akun uji")
    parser.add_argument("--url-tugas", help="Alamat halaman tugas yang dipakai uji unggah")
    return parser.parse_args()


def terapkan_override(args: argparse.Namespace) -> None:
    # Nilai dari baris perintah lebih tinggi prioritasnya daripada berkas .env.
    pasangan = {
        "SUNAN_URL": args.url,
        "SUNAN_PENGGUNA": args.pengguna,
        "SUNAN_SANDI": args.sandi,
        "SUNAN_URL_TUGAS": args.url_tugas,
        "BROWSER_UJI": args.browser,
    }
    for kunci, nilai in pasangan.items():
        if nilai:
            os.environ[kunci] = nilai
    if args.headed:
        os.environ["HEADLESS"] = "0"
    if args.login_manual:
        os.environ["HEADLESS"] = "0"
        os.environ["LOGIN_MANUAL"] = "1"


def kunci_pilihan(daftar_id: str) -> str:
    # Mengubah daftar ID test case menjadi penapis pytest (-k).
    kunci = []
    for id_uji in daftar_id.split(","):
        id_uji = id_uji.strip().lower()
        if id_uji:
            kunci.append(id_uji.replace("-", "_"))
    return " or ".join(kunci)


def pisahkan_pilihan(daftar_id: str) -> tuple[list[str], list[str]]:
    # Memisahkan ID pilihan menjadi yang dikerjakan otomatis dan yang manual.
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
    print(GARIS)
    for id_uji, skenario, cara in DAFTAR_TEST_CASE:
        print(f"{id_uji} | {cara:<8} | {skenario}")
    print(GARIS)


def cetak_kepala(konfigurasi) -> None:
    mode = "headless" if konfigurasi.headless else "headful"
    print()
    print(GARIS)
    print("PENGUJIAN OTOMATIS - SUNAN UMK")
    print(f"  situs    : {konfigurasi.url}")
    print(f"  browser  : {', '.join(konfigurasi.browser)}")
    print(f"  mode     : {mode}")
    print(GARIS)


def jalankan_pytest(konfigurasi, nama_browser: str, otomatis: list[str]) -> int:
    junit = konfigurasi.folder_hasil / f"junit_{nama_browser}.xml"
    perintah = [
        sys.executable,
        "-m",
        "pytest",
        "src/uji",
        "-q",
        "-s",
        "--no-header",
        "-p",
        "no:cacheprovider",
        f"--junitxml={junit}",
    ]
    if otomatis:
        perintah += ["-k", kunci_pilihan(",".join(otomatis))]
    lingkungan = dict(os.environ, BROWSER_UJI=nama_browser)
    catatan = konfigurasi.folder_hasil / f"pytest_{nama_browser}.log"
    with catatan.open("w", encoding="utf-8") as keluaran:
        selesai = subprocess.run(perintah, cwd=AKAR, env=lingkungan, stdout=keluaran)
    return selesai.returncode


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
    logger = siapkan_log(konfigurasi.folder_hasil, ke_konsol=False)
    siapkan_berkas(konfigurasi.folder_berkas, konfigurasi.batas_unggah_mb)

    if args.buat_berkas:
        logger.info("Berkas uji siap di %s", konfigurasi.folder_berkas)
        print(f"Berkas uji siap di {konfigurasi.folder_berkas}")
        return 0

    if not konfigurasi.punya_kredensial and not ambil_benar("LOGIN_MANUAL", False):
        print()
        print("Catatan: kredensial akun mahasiswa belum diisi, skenario akan dilewati.")
        print("        Isi SUNAN_PENGGUNA dan SUNAN_SANDI di berkas .env,")
        print("        atau jalankan dengan --login-manual.")
    if not konfigurasi.url_tugas:
        print("Catatan: SUNAN_URL_TUGAS belum diisi, uji unggah berkas tidak bisa jalan.")
    print()

    otomatis, manual = ([], [])
    if args.pilih:
        otomatis, manual = pisahkan_pilihan(args.pilih)
        if manual:
            skenario_manual(manual)
        if not otomatis:
            return 0

    cetak_kepala(konfigurasi)
    kode_keluar = 0
    rekap = []
    total = len(konfigurasi.browser)

    for nomor, nama_browser in enumerate(konfigurasi.browser, start=1):
        os.environ["BROWSER_UJI"] = nama_browser
        biner = cari_biner(nama_browser, konfigurasi)
        print(f"[{nomor}/{total}] {nama_browser}")
        sys.stdout.flush()

        kode = jalankan_pytest(konfigurasi, nama_browser, otomatis)
        kode_keluar = kode_keluar or kode

        junit = konfigurasi.folder_hasil / f"junit_{nama_browser}.xml"
        jumlah = baca_hasil(junit)
        tulis_laporan(junit, konfigurasi.folder_hasil, konfigurasi, nama_browser, biner)
        rekap.append((nama_browser, jumlah))
        print(
            f"        {jumlah['lulus']} lulus  {jumlah['gagal']} gagal  "
            f"{jumlah['dilewati']} dilewati   ->  hasil/laporan_{nama_browser}.txt"
        )

    laporan_gabungan = _gabungkan_laporan(konfigurasi)
    print()
    print(GARIS)
    print("RINGKASAN")
    for nama_browser, jumlah in rekap:
        print(
            f"  {nama_browser:<8} {jumlah['lulus']} lulus  {jumlah['gagal']} gagal  "
            f"{jumlah['dilewati']} dilewati"
        )
    jumlah_total = {"lulus": 0, "gagal": 0, "dilewati": 0}
    for _, jumlah in rekap:
        for kunci, nilai in jumlah.items():
            jumlah_total[kunci] += nilai
    print(
        f"  {'total':<8} {jumlah_total['lulus']} lulus  {jumlah_total['gagal']} gagal  "
        f"{jumlah_total['dilewati']} dilewati"
    )
    print(GARIS)
    print(f"Laporan lengkap: {laporan_gabungan}")
    return int(kode_keluar)


def _gabungkan_laporan(konfigurasi) -> Path:
    # Menyatukan laporan per browser menjadi satu berkas ringkasan.
    folder = konfigurasi.folder_hasil
    bagian = []
    for nama_browser in konfigurasi.browser:
        berkas = folder / f"laporan_{nama_browser}.txt"
        if berkas.exists():
            bagian.append(berkas.read_text(encoding="utf-8"))
    tujuan = folder / "laporan_pengujian.txt"
    tujuan.write_text("\n".join(bagian), encoding="utf-8")
    return tujuan


if __name__ == "__main__":
    sys.exit(main())
