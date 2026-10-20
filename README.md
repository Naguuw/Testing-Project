# Pengujian Otomatis Sunan UMK

Pengujian otomatis website e-learning Sunan UMK (`sunan.umk.ac.id`) memakai
Selenium dan pytest. Test case, teknik black-box, dan data uji mengikuti
dokumen *Perancangan dan Pengujian Website E* serta `test-plan-elearning.md`.


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
│   ├── materi_valid.pdf         PDF biasa untuk uji unggah berhasil
│   ├── materi_batas_bawah.pdf   satu byte di bawah batas ukuran
│   ├── materi_batas_tepat.pdf   tepat pada batas ukuran
│   ├── berkas_0_byte.bin        berkas kosong, harus ditolak
│   ├── berkas_ilegal.exe        berkas tiruan berekstensi terlarang
│   └── duplikat/
│       ├── satu/materi.pdf      dua berkas bernama sama
│       └── dua/materi.pdf
├── hasil/                   keluaran pengujian, dibuat otomatis
│   ├── pengujian.log            catatan jalannya skenario
│   ├── junit_<browser>.xml     hasil mentah format JUnit
│   ├── laporan_<browser>.txt   ringkasan per browser
│   ├── laporan_pengujian.txt    gabungan seluruh browser
│   └── foto/                    tangkapan layar bukti
└── src/
    ├── __init__.py
    ├── konfigurasi.py       pembacaan .env dan daftar browser
    ├── browser.py           pembuatan driver tiap browser
    ├── data_uji.py          pembuat berkas uji
    ├── pelapor.py           log, tangkapan layar, dan laporan
    ├── halaman/
    │   ├── __init__.py
    │   ├── dasar.py         pencarian elemen yang tahan perubahan tampilan
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


## Konfigurasi

Salin `.env.example` menjadi `.env`, lalu isi:

```
SUNAN_URL=https://sunan.umk.ac.id
SUNAN_PENGGUNA=1234567890
SUNAN_SANDI=kata_sandi
SUNAN_URL_TUGAS=https://sunan.umk.ac.id/mod/assign/view.php?id=12345

BROWSER_UJI=chrome,firefox,edge
HEADLESS=1
BATAS_UNGGAH_MB=5
```

| Kunci | Isi |
|---|---|
| `SUNAN_URL` | Alamat situs yang diuji |
| `SUNAN_PENGGUNA`, `SUNAN_SANDI` | Kredensial akun mahasiswa uji |
| `SUNAN_URL_TUGAS` | Alamat halaman tugas untuk uji unggah berkas |
| `BROWSER_UJI` | Browser yang diuji, dipisah koma |
| `HEADLESS` | `1` tanpa jendela browser, `0` dengan jendela |
| `BATAS_UNGGAH_MB` | Batas ukuran unggah yang diuji, mengikuti BR-01 (5 MB) |
| `BINER_CHROME`, `BINER_FIREFOX`, `BINER_EDGE` | Lokasi browser, isi bila tidak ditemukan otomatis |
| `DRIVER_CHROME`, `DRIVER_FIREFOX`, `DRIVER_EDGE` | Lokasi web driver, isi bila tidak ditemukan otomatis |

Seluruh kunci `BINER_*` dan `DRIVER_*` boleh dibiarkan kosong. Yang diisi hanya
perlu pada Linux yang tidak punya Chrome, Firefox, maupun Edge.

## Cara Menjalankan

### Windows

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Perintah lain:

```
python main.py --browser chrome
python main.py --headed
python main.py --login-manual
python main.py --pilih TC-LGN-01
python main.py --panduan
```

### Linux

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Bila memakai browser yang tidak terpasang di sistem, isi `BINER_*` dan
`DRIVER_*` di `.env` dengan lokasi berkas yang sebenarnya.

## Alur Pengujian

1. `main.py` membaca `.env`, menyiapkan berkas uji, lalu menjalankan pytest
   sekali untuk setiap browser di `BROWSER_UJI`.
2. Untuk tiap browser, skenario login membuka halaman `sunan.umk.ac.id`,
   mengisi kredensial, lalu memeriksa ada tidaknya reCAPTCHA.
3. Bila ada reCAPTCHA, skenario menunggu checkbox dicentang. Pada mode
   `--headed` orang yang menguji cukup mencocokkan checkbox di jendela browser;
   skenario lanjut sendiri setelah respons terisi. Tanpa itu skenario
   ditandai terhalang (dilewati), bukan gagal.
4. Setelah masuk, skenario membuka halaman tugas, mengunggah berkas uji, lalu
   memeriksa hasilnya: berkas diterima, ditolak, atau statusnya berubah.
5. Hasil tiap browser ditulis pada `hasil/` sebagai log, JUnit XML, dan
   laporan teks.

## Soal CAPTCHA

reCAPTCHA pada halaman login **tidak dilewati secara otomatis**. Widget-nya
memakai reCAPTCHA Enterprise dengan centang "bukan robot", dan satu-satunya
jalur yang sah adalah checkbox dicentang manusia. Yang dilakukan otomatisi
hanya:

- Mendeteksi bahwa reCAPTCHA ada di halaman.
- Menunggu sampai medan `g-recaptcha-response` terisi, yang menandakan
  captcha sudah terpecahkan.
- Melanjutkan skenario secara otomatis setelah itu.

Akibatnya:

| Situasi | Hasil skenario |
|---|---|
| `--headed`, checkbox dicentang | Skenario berjalan seperti biasa |
| `--headed`, checkbox tidak dicentang sampai batas waktu | Dilewati (terhalang) |
| Tanpa `--headed` | Dilewati (terhalang), karena tidak ada yang bisa mencocokkan |

Keterbatasan ini memang dicatat pada dokumen rencana pengujian, bahwa
otomasi terhambat oleh captcha. Dengan satu akun uji dan satu browser,
prosesnya cukup: jalankan `python main.py --headed`, cocokkan checkbox,
lalu biarkan skenario berjalan sendiri.

Kalau ingin login sendiri sepenuhnya, pakai `python main.py --login-manual`.
Skrip membuka jendela browser lalu menunggu kamu selesai login (username,
password, dan centang CAPTCHA).Begitu sesi terdeteksi, skenario `TC-TGS-*`
langsung berjalan tanpa campur lagi, dan kredensial di `.env` tidak perlu
diisi.

## Catatan untuk Linux

Chrome, Firefox, dan Edge sudah dipasang di mesin ini, sehingga `.env` tinggal
menunjuk lokasi biner dan web driver. Bila perlu memasang ulang di Linux lain:

```
# Firefox portable
curl -sSL -o /tmp/firefox.tar.xz "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US"
tar -xf /tmp/firefox.tar.xz -C ~/.local/opt/

# geckodriver
curl -sSL -o /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz"
tar -xzf /tmp/geckodriver.tar.gz -C ~/.local/bin/

# chromedriver (sesuaikan versinya dengan Chrome yang terpasang)
npx @puppeteer/browsers install chromedriver@stable
```

Chrome, Chromium, atau Brave memakai chromedriver yang versinya harus sama
dengan browser. Selenium Manager sudah menangani pencocokan versi ini sendiri,
sehingga unduhan manual hanya perlu bila `DRIVER_*` dikosongkan tetapi
Selenium Manager gagal mengunduhnya.

## Keluarannya

| Berkas | Isi |
|---|---|
| `hasil/pengujian.log` | Catatan jalannya setiap skenario |
| `hasil/junit_<browser>.xml` | Hasil mentah format JUnit per browser |
| `hasil/laporan_<browser>.txt` | Ringkasan per test case per browser |
| `hasil/laporan_pengujian.txt` | Gabungan laporan dari semua browser |
| `hasil/foto/` | Tangkapan layar bukti |

## Test Case Otomatis

| ID | Skenario | Browser |
|---|---|---|
| TC-LGN-01 | Login dengan kredensial valid | Semua |
| TC-LGN-02 | Login dengan kredensial tidak valid | Semua |
| TC-TGS-01 | Unggah tugas format PDF valid | Semua |
| TC-TGS-02 | Ukuran di bawah dan tepat pada batas | Semua |
| TC-TGS-03 | Berkas kosong (0 byte) | Semua |
| TC-TGS-05 | Format tidak diizinkan | Semua |

Skenario manual (TC-MKL-01, TC-TGS-04, TC-TGS-06, TC-AKS-01) beserta
langkahnya tersedia lewat `python main.py --panduan`.

## Keterbatasan

- Halaman login memakai reCAPTCHA, sehingga selalu butuh satu sentuhan
  manusia. Headless tanpa interaksi akan menandai skenario sebagai terhalang.
- Otomasi tidak menilai kejelasan tampilan, sehingga pesan error, daftar nilai,
  dan unduhan materi tetap diperiksa manual.
- Skenario yang bergantung pada gangguan jaringan dan dialog nama berkas sama
  dikerjakan manual karena sulit ditiru skrip.
- Pengujian pada dokumen dilaporkan dari satu browser saja, sehingga hasilnya
  belum dapat digeneralisasi untuk seluruh lingkungan.
