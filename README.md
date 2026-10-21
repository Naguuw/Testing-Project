# Pengujian Otomatis Sunan UMK

Pengujian otomatis website e-learning Sunan UMK (`sunan.umk.ac.id`) memakai
Selenium dan pytest. Test case, teknik black-box, dan data uji mengikuti
dokumen *Perancangan dan Pengujian Website E* dan `test-plan-elearning.md`.

## Struktur Folder

```
Ini Folder Ygy
├── main.py                  titik eksekusi
├── pytest.ini               pengaturan pytest
├── requirements.txt         daftar dependensi
├── test-plan-elearning.md   rencana pengujian
├── README.md                dokumen ini
├── .env                     konfigurasi lokal
├── .env.example             contoh konfigurasi
├── .gitignore
├── berkas/                  berkas uji, dibuat otomatis
│   ├── README.md
│   ├── materi_valid.pdf         PDF biasa untuk uji upload berhasil
│   ├── materi_batas_bawah.pdf   satu byte di bawah batas ukuran
│   ├── materi_batas_tepat.pdf   tepat pada batas ukuran
│   ├── berkas_0_byte.bin        berkas kosong, harus ditolak
│   ├── berkas_ilegal.exe        berkas tiruan berekstensi terlarang
│   └── duplikat/
│       ├── satu/materi.pdf      dua berkas bernama sama
│       └── dua/materi.pdf
├── hasil/                   keluaran pengujian, dibuat otomatis
│   ├── pengujian_<browser>.log    catatan jalannya skenario
│   ├── pytest_<browser>.log       keluaran mentah pytest
│   ├── junit_<browser>.xml        hasil format JUnit
│   ├── laporan_<browser>.txt      ringkasan per browser
│   ├── laporan_pengujian.txt      gabungan semua browser
│   └── bukti/                    screenshot dan cuplikan DOM saat gagal
└── src/
    ├── __init__.py
    ├── konfigurasi.py       pembacaan .env dan daftar browser
    ├── browser.py           pembuatan driver tiap browser
    ├── data_uji.py          pembuat berkas uji
    ├── pelapor.py           log, bukti kegagalan, dan laporan
    ├── halaman/
    │   ├── __init__.py
    │   ├── dasar.py         pencarian elemen dengan selector kandidat
    │   ├── login.py         halaman login
    │   └── tugas.py         halaman pengumpulan tugas
    └── uji/
        ├── __init__.py
        ├── conftest.py      fixture bersama
        ├── test_login.py    TC-LGN-01 dan TC-LGN-02
        ├── test_tugas.py    TC-TGS-01, TC-TGS-02, TC-TGS-03, TC-TGS-05
        └── panduan_manual.py skenario uji manual
```

## Yang Perlu Disiapkan

| Kebutuhan | Keterangan |
|---|---|
| Python 3.10 atau lebih baru | Sudah termasuk di dalam venv |
| Akun mahasiswa uji | Dipakai pada seluruh skenario otomatis |
| Satu browser | Chrome, Firefox, atau Edge, sesuai `BROWSER_UJI` di `.env` |

Web driver tidak perlu diunduh manual. Selenium Manager mengunduh driver yang
cocok dengan versi browser saat pertama kali skenario dijalankan, selama mesin
punya koneksi internet.

## Konfigurasi

Salin `.env.example` menjadi `.env`, lalu isi:

```
SUNAN_URL=https://sunan.umk.ac.id
SUNAN_PENGGUNA=1234567890
SUNAN_SANDI=kata_sandi
SUNAN_URL_TUGAS=https://sunan.umk.ac.id/mod/assign/view.php?id=710123&action=editsubmission

BROWSER_UJI=chrome,firefox,edge
HEADLESS=1
BATAS_UPLOAD_MB=5
```

| Kunci | Isi |
|---|---|
| `SUNAN_URL` | Alamat situs yang diuji, boleh ditulis tanpa `/login/index.php` |
| `SUNAN_PENGGUNA`, `SUNAN_SANDI` | Kredensial akun mahasiswa uji |
| `SUNAN_URL_TUGAS` | Alamat halaman tugas untuk uji upload berkas |
| `BROWSER_UJI` | Browser yang diuji, dipisah koma |
| `HEADLESS` | `1` tanpa jendela browser, `0` dengan jendela |
| `BATAS_UPLOAD_MB` | Batas ukuran upload yang diuji, mengikuti BR-01 (5 MB) |
| `BINER_CHROME`, `BINER_FIREFOX`, `BINER_EDGE` | Lokasi browser, isi bila tidak ditemukan otomatis |
| `DRIVER_CHROME`, `DRIVER_FIREFOX`, `DRIVER_EDGE` | Lokasi web driver, isi bila tidak ditemukan otomatis |
| `WAKTU_TUNGGU` | Batas waktu menunggu elemen, default 30 detik |
| `WAKTU_CAPTCHA` | Batas waktu menunggu centang CAPTCHA, default 120 detik |
| `WAKTU_LOGIN_MANUAL` | Batas waktu menunggu login manual, default 300 detik |
| `WAKTU_UPLOAD` | Batas waktu menunggu berkas besar terupload, default 90 detik |

Kunci `BINER_*` dan `DRIVER_*` boleh dikosongkan. Mengisinya hanya perlu pada
sistem yang tidak punya browser tersebut.

### Dua alamat yang perlu diperhatikan

**Halaman login.** `SUNAN_URL` boleh diisi `https://sunan.umk.ac.id` saja.
Beranda hanya punya form login di dalam modal tanpa tombol ber-ID `loginbtn`,
sedangkan halaman login (`/login/index.php`) punya tombol itu. Kode
menambahkan `/login/index.php` bila alamat yang diisi tidak punya path.

**Halaman tugas.** Salin alamat dari browser saat sudah membuka halaman tugas:

```
https://sunan.umk.ac.id/mod/assign/view.php?id=710123&action=editsubmission
```

Bagian `action=editsubmission` yang menampilkan form upload. Kalau alamat yang
disalin belum memuat bagian itu, kodenya menambahkannya sendiri.

Batas yang berlaku di situs:

| Aturan | Nilai |
|---|---|
| Ukuran maksimum berkas | 20 MB |
| Jumlah berkas maksimum | 1 |
| Tipe berkas yang diterima | .doc, .docx, .pdf, .rtf |

## Cara Menjalankan

### Windows

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Linux

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Perintah lain:

```
python main.py --browser chrome            jalankan hanya di satu browser
python main.py --headed                   tampilkan jendela browser
python main.py --login-manual             login sendiri di jendela browser
python main.py --pilih TC-LGN-01          jalankan test case tertentu
python main.py --panduan                  tampilkan skenario uji manual
python main.py --daftar                   tampilkan daftar test case
```

Bila browser yang dipilih tidak terpasang di sistem, isi `BINER_*` dan
`DRIVER_*` di `.env` dengan lokasi berkasnya.

## Cara Kerja Upload Berkas

Moodle memakai modal **File picker**, jadi uploadan berjalan berjenjang:

1. Buka halaman tugas dengan `action=editsubmission`
2. Klik tombol "Add..." di toolbar file manager
3. Isi field "Choose File" dan kolom "Save as"
4. Klik "Upload this file"

Tombol "Upload this file" adalah titik keputusan. Di situ sistem memberi tahu
berkas diterima atau ditolak.

Pengujian otomatis **berhenti setelah berkas terlampir**. Tombol "Save changes"
sengaja tidak ditekan, karena itu mengirim pengumpulan mahasiswa dan akan
terlihat oleh dosen. Pemeriksaan "Submission status: Submitted for grading"
dilakukan manual, caranya ada di `python main.py --panduan`.

Selector memakai `name` dan `class`, bukan `id` Moodle yang berubah-ubah
setiap halaman dimuat.

## Soal CAPTCHA

reCAPTCHA pada halaman login tidak dilewati secara otomatis. Widget-nya memakai
reCAPTCHA Enterprise dengan centang "bukan robot", dan satu-satunya jalur yang
sah adalah checkbox dicentang manusia. Yang dilakukan otomatisi hanya:

- Mendeteksi reCAPTCHA di halaman
- Menunggu sampai checkbox tercentang, yang ditandai median respons terisi
- Melanjutkan skenario setelah itu

| Situasi | Hasil skenario |
|---|---|
| `--headed`, checkbox dicentang | Skenario berjalan seperti biasa |
| `--headed`, checkbox tidak dicentang sampai batas waktu | Dilewati (terhalang) |
| Tanpa `--headed` | Dilewati (terhalang), tidak ada yang bisa mencocokkan |

Untuk login sepenuhnya manual, pakai `python main.py --login-manual`. Skrip
membuka jendela browser lalu menunggu kamu selesai login. Sesi yang berhasil
disimpan, jadi skenario berikutnya tidak perlu mencocokkan CAPTCHA lagi.

## Keluaran

| Berkas | Isi |
|---|---|
| `hasil/pengujian_<browser>.log` | Catatan jalannya setiap skenario |
| `hasil/pytest_<browser>.log` | Keluaran mentah pytest |
| `hasil/junit_<browser>.xml` | Hasil format JUnit |
| `hasil/laporan_<browser>.txt` | Ringkasan per test case |
| `hasil/laporan_pengujian.txt` | Gabungan semua browser |
| `hasil/bukti/` | Screenshot dan cuplikan DOM setiap test yang gagal |

## Test Case Otomatis

| ID | Skenario |
|---|---|
| TC-LGN-01 | Login dengan kredensial valid |
| TC-LGN-02 | Login dengan kredensial tidak valid |
| TC-TGS-01 | Upload tugas format PDF valid |
| TC-TGS-02 | Ukuran di bawah dan tepat pada batas |
| TC-TGS-03 | Berkas kosong (0 byte) |
| TC-TGS-05 | Format tidak diizinkan |

Skenario manual (TC-MKL-01, TC-TGS-04, TC-TGS-06, TC-AKS-01) beserta
langkahnya tersedia lewat `python main.py --panduan`.

## Memasang Browser di Linux

Chrome, Firefox, dan Edge bisa dipasang manual. Contoh untuk Firefox dan
geckodriver:

```
curl -sSL -o /tmp/firefox.tar.xz "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US"
tar -xf /tmp/firefox.tar.xz -C ~/.local/opt/

curl -sSL -o /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"
tar -xzf /tmp/geckodriver.tar.gz -C ~/.local/bin/
```

Chrome, Chromium, dan Brave memakai chromedriver dengan versi yang sama dengan
browsernya. Selenium Manager sudah menangani pencocokan versi ini sendiri,
jadi unduhan manual hanya perlu bila `DRIVER_*` dikosongkan dan Selenium
Manager gagal mengunduhnya.

## Keterbatasan

- Halaman login memakai reCAPTCHA, jadi selalu butuh satu sentuhan manusia.
  Headless tanpa interaksi akan menandai skenario sebagai terhalang.
- Otomasi tidak menilai kejelasan tampilan, sehingga pesan error, daftar nilai,
  dan unduhan materi tetap diperiksa manual.
- Skenario yang bergantung pada gangguan jaringan dan dialog nama berkas sama
  dikerjakan manual karena sulit ditiru skrip.
- Pengujian pada dokumen dilaporkan dari satu browser saja, sehingga hasilnya
  belum dapat digeneralisasi untuk seluruh lingkungan.
