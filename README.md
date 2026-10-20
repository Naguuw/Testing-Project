# Pengujian Otomatis Sunan UMK

Proyek ini menjalankan test case pengujian website e-learning Sunan UMK
(`sunan.umk.ac.id`) dengan Selenium. Test case, teknik black-box, dan data uji
mengikuti dokumen *Perancangan dan Pengujian Website E* dan
`test-plan-elearning.md`.

## Struktur Folder

```
main.py                 titik eksekusi seluruh pengujian
pytest.ini              pengaturan pytest
requirements.txt        daftar dependensi
.env                    konfigurasi lokal (jangan ikut dibagikan)
berkas/                 berkas uji (dibuat otomatis)
hasil/                  log, tangkapan layar, dan laporan
src/
  konfigurasi.py        pembacaan .env
  browser.py            pembuatan driver Chrome/Chromium/Brave
  data_uji.py           pembuat berkas uji
  pelapor.py            log, screenshot, dan laporan akhir
  halaman/              locator dan alur tiap halaman
    dasar.py            pencarian elemen yang tahan perubahan tampilan
    login.py            halaman login
    tugas.py            halaman pengumpulan tugas
  uji/                  test case pytest
    conftest.py         fixture bersama
    test_login.py       TC-LGN-01 dan TC-LGN-02
    test_tugas.py       TC-TGS-01, TC-TGS-02, TC-TGS-03, TC-TGS-05
    panduan_manual.py   skenario uji manual
```

## Persiapan

```bash
source /home/nagisa/.venvs/bin/activate
pip install -r requirements.txt
```

Isi kredensial akun mahasiswa uji pada berkas `.env`:

```
SUNAN_PENGGUNA=1234567890
SUNAN_SANDI=kata_sandi
SUNAN_URL_TUGAS=https://sunan.umk.ac.id/mod/assign/view.php?id=12345
```

`SUNAN_URL_TUGAS` adalah alamat halaman tugas yang dipakai uji unggah berkas.
`BROWSER_BINARY` dan `CHROMEDRIVER_PATH` boleh dikosongkan bila Chrome dan
chromedriver sudah ada di sistem.

## Untuk anggota tim

Berkas `.env` tidak ikut dibagikan karena berisi kredensial akun uji. Setiap
anggota membuat salinannya sendiri:

```bash
git clone <alamat-repo> modul-5
cd modul-5
cp .env.example .env
$EDITOR .env
```

Isi `SUNAN_PENGGUNA`, `SUNAN_SANDI`, dan `SUNAN_URL_TUGAS` memakai akun uji
milikmu sendiri. `BROWSER_BINARY` dan `CHROMEDRIVER_PATH` biarkan kosong
lalu; isi hanya bila Chrome tidak terdeteksi otomatis di mesinmu.

Berkas uji pada folder `berkas/` dan seluruh keluaran pada folder `hasil/`
dibuat otomatis, jadi tidak perlu dikirim. Yang ikut ke repository hanya
source code, `test-plan-elearning.md`, dan `.env.example`.

Kalau memakai zip, kirim folder tanpa `.env` dan tanpa `hasil/`.

## Menjalankan

```bash
python main.py                     # seluruh test case otomatis
python main.py --headed            # tampilkan browser, untuk CAPTCHA manual
python main.py --pilih TC-LGN-01   # jalankan test case tertentu
python main.py --daftar            # daftar test case
python main.py --panduan           # skenario uji manual
python main.py --buat-berkas       # siapkan berkas uji saja
```

## Keluaran

| Berkas | Isi |
|---|---|
| `hasil/pengujian.log` | Catatan jalannya setiap skenario |
| `hasil/junit.xml` | Hasil mentah format JUnit |
| `hasil/laporan_pengujian.txt` | Ringkasan per test case dan jumlahnya |
| `hasil/foto/` | Tangkapan layar bukti |

## Keterbatasan

- Halaman login memakai reCAPTCHA. Pada mode `--headed` operator perlu
  mencocokkan CAPTCHA di jendela browser; tanpa itu skenario ditandai terhalang
  (dilewati), bukan gagal.
- Otomasi tidak menilai kejelasan tampilan, sehingga pesan galat, daftar nilai,
  dan unduhan materi tetap diperiksa manual.
- Skenario yang bergantung pada gangguan jaringan (koneksi terputus) dan
  dialog nama berkas sama dikerjakan manual karena sulit ditiru skrip.
