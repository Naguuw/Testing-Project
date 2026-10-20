# Skenario uji manual yang tidak dikerjakan Selenium.

from __future__ import annotations

SKENARIO_MANUAL = [
    (
        "TC-MKL-01",
        "Mata Kuliah",
        "Login sebagai mahasiswa uji, klik satu mata kuliah, buka salah satu topiknya, "
        "lalu unduh satu berkas materi. Pastikan halaman lengkap dan berkas bisa dibuka.",
    ),
    (
        "TC-TGS-04",
        "Tugas",
        "Mulai mengunggah berkas, matikan Wi-Fi di tengah proses, lalu sambungkan kembali. "
        "Perhatikan pesan error dan apakah pengumpulan setengah jadi tersimpan.",
    ),
    (
        "TC-TGS-06",
        "Tugas",
        "Unggah satu PDF lewat File picker > Upload a file, lalu unggah PDF lain dengan nama sama. "
        "Periksa dialog File exists (Overwrite, Rename, Cancel).",
    ),
    (
        "TC-AKS-01",
        "Penilaian",
        "Login sebagai mahasiswa uji, lalu buka halaman Grades (Home > Dashboard > Grades). "
        "Periksa nama mahasiswa dan daftar nilai mata kuliah yang diikutinya.",
    ),
    (
        "NFR-01",
        "Kompatibilitas",
        "Ulangi skenario login dan unggah tugas pada Chrome, Firefox, dan Edge.",
    ),
    (
        "NFR-02",
        "Kinerja",
        "Catat waktu muat halaman login, dasbor, dan halaman mata kuliah pada koneksi stabil.",
    ),
    (
        "NFR-03",
        "Keamanan Dasar",
        "Periksa alamat memakai HTTPS dan halaman terproteksi tidak terbuka lewat tombol Back.",
    ),
    (
        "NFR-04",
        "Keandalan",
        "Ulangi skenario login dan unggah beberapa kali, bandingkan hasilnya.",
    ),
]


def cetak_panduan() -> None:
    print()
    print("SKENARIO UJI MANUAL")
    print("=" * 72)
    for id_uji, fitur, langkah in SKENARIO_MANUAL:
        print(f"{id_uji} | {fitur}")
        print(f"   {langkah}")
        print("-" * 72)


def skenario_manual(daftar_id: list[str]) -> None:
    print()
    print("SKENARIO UJI MANUAL")
    print("=" * 72)
    for id_uji, fitur, langkah in SKENARIO_MANUAL:
        if id_uji in daftar_id:
            print(f"{id_uji} | {fitur}")
            print(f"   {langkah}")
            print("-" * 72)
