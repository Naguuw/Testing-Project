# Berkas uji

Folder ini berisi berkas yang dipakai pengujian upload tugas. Semua berkas
dibuat otomatis oleh `main.py` lewat `src/data_uji.py`, jadi tidak perlu
disalin manual.

| Berkas | Dipakai pada | Keterangan |
|---|---|---|
| `materi_valid.pdf` | TC-TGS-01 | PDF normal untuk uji upload berhasil |
| `materi_batas_bawah.pdf` | TC-TGS-02 | Ukuran satu byte di bawah batas (5.242.879 byte) |
| `materi_batas_tepat.pdf` | TC-TGS-02 | Ukuran tepat pada batas (5.242.880 byte) |
| `berkas_0_byte.bin` | TC-TGS-03 | Berkas kosong, harus ditolak sistem |
| `berkas_ilegal.exe` | TC-TGS-05 | Berkas tiruan berekstensi terlarang, aman untuk dijalankan |
| `duplikat/satu/materi.pdf` | TC-TGS-06 | Dua berkas bernama sama, dipakai uji manual |
| `duplikat/dua/materi.pdf` | TC-TGS-06 | Dua berkas bernama sama, dipakai uji manual |

Batas ukuran mengikuti `BATAS_UPLOAD_MB` di berkas `.env`. Mengubah nilai itu
mengulang pembuatan berkas dengan ukuran batas yang baru.
