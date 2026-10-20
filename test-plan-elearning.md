# Rencana Pengujian: Website E-Learning Sunan UMK (sunan.umk.ac.id)

Dokumen acuan: *Perancangan dan Pengujian Website E* (`Perancangan dan Pengujian Website E.docx`).
Rencana ini disusun selaras dengan dokumen tersebut: objek uji, ruang lingkup, teknik black-box, data uji, dan 10 test case yang diturunkan di dalamnya.

---

## 1. Pendahuluan

### 1.1 Latar Belakang

Pengujian perangkat lunak adalah proses untuk memastikan sebuah aplikasi bekerja sesuai spesifikasi dan tidak menimbulkan kesalahan yang merugikan pengguna. Pada aplikasi e-learning, kesalahan validasi input dan kegagalan unggah berkas dapat langsung mengganggu proses belajar (Agustian et al., 2020; Akbar et al., 2025).

Sunan UMK (sunan.umk.ac.id) adalah platform e-learning Universitas Muria Kudus yang digunakan mahasiswa untuk mengakses mata kuliah, mengunduh materi, mengumpulkan tugas, dan melihat nilai. Tampilan dan istilah antarmukanya (misalnya *My courses*, *Submitted for grading*, *File picker*) menunjukkan bahwa platform ini kemungkinan berbasis Moodle.

### 1.2 Tujuan

Menyusun rencana serta melaksanakan pengujian fungsional dan non-fungsional pada website Sunan UMK dengan pendekatan black-box, dan menggunakan pengujian otomasi Selenium sebagai alternatif pengujian.

### 1.3 Ruang Lingkup

**Diuji:**

- Login mahasiswa dengan kredensial valid dan tidak valid.
- Akses mata kuliah dan unduh materi.
- Pengumpulan tugas melalui unggah berkas (validasi format, ukuran, nama berkas, dan kondisi koneksi terputus).
- Halaman penilaian (*Grades*).
- Pengujian non-fungsional: kinerja, kompatibilitas, keamanan dasar, dan keandalan.

**Tidak diuji:**

- Uji beban (*load*) berat dan uji penetrasi keamanan.
- Fitur logout dan lupa password sebagai fitur (yang diperiksa hanyalah perilaku sesi, lihat catatan di §4.3).
- Fitur di luar cakupan paper: kuis, forum, notifikasi/pengumuman, pengelolaan profil, pendaftaran/enroll mata kuliah, pemutaran video materi, dan pencatatan progres belajar.
- Pengujian pada role selain mahasiswa (dosen/admin), karena akun uji yang tersedia hanya akun mahasiswa.

> **Catatan.** Test case pada rencana ini memakai ID yang sama dengan dokumen acuan (`TC-LGN-*`, `TC-MKL-*`, `TC-TGS-*`, `TC-AKS-*`) sehingga hasil eksekusi dapat ditelusuri satu-satu ke tabel test case pada paper.

### 1.4 Objek Uji

LMS Sunan Universitas Muria Kudus, URL `sunan.umk.ac.id`, berupa aplikasi web (kemungkinan berbasis Moodle) yang diakses melalui browser desktop.

### 1.5 Manfaat

Hasil pengujian menjadi masukan perbaikan bagi pengelola Sunan UMK, khususnya pada penanganan galat unggah. Bagi mahasiswa penguji, rencana ini melatih penyusunan rencana uji, penurunan test case dengan teknik black-box, dan pemanfaatan otomasi untuk pengujian regresi.

---

## 2. Kebutuhan Data Uji

| Kode | Data uji | Keterangan |
|---|---|---|
| D-01 | Akun mahasiswa valid | Dipakai pada seluruh skenario yang memerlukan sesi masuk |
| D-02 | Username valid + password salah | Kelas tidak valid untuk login |
| D-03 | Berkas PDF valid | Berkas materi/unggah normal |
| D-04 | PDF 5.242.879 byte dan 5.242.880 byte | Nilai batas bawah dan tepat 5 MB (lihat `TC-TGS-02`) |
| D-05 | Berkas 0 byte (`berkas_0_byte.bin`) | Batas bawah ukuran berkas |
| D-06 | Berkas tiruan tidak berbahaya berekstensi `.exe` | Format tidak diizinkan |
| D-07 | Dua berkas PDF dengan nama sama | Deteksi nama ganda saat mengunggah |
| D-08 | Skenario koneksi terputus | Wi-Fi dimatikan di tengah proses unggah |

---

## 3. Metode Pengujian

### 3.1 Verifikasi dan Validasi

Verifikasi memeriksa apakah produk dibangun dengan benar sesuai spesifikasi, sedangkan validasi memeriksa apakah produk yang dibangun benar-benar memenuhi kebutuhan pengguna. Pengujian pada paper ini berada pada sisi validasi karena dilakukan dari sudut pandang mahasiswa sebagai pengguna akhir, dan sekaligus merupakan verifikasi dinamis karena perilaku sistem yang berjalan dibandingkan dengan hasil yang diharapkan.

### 3.2 Alasan Memilih Black Box

Kode sumber Sunan UMK tidak dapat diakses oleh penguji. Black-box berfokus pada masukan dan keluaran sehingga sesuai untuk aplikasi web yang sudah berjalan dan untuk memeriksa kebutuhan fungsional (Akbar et al., 2025; Saputra & Jatmiko, 2024).

### 3.3 Teknik Black Box yang Dipakai

| Teknik | Fungsi | Contoh pada rencana ini |
|---|---|---|
| Use Case Testing (UC) | Menurunkan kasus uji dari alur utama dan alur alternatif sebuah use case | `TC-MKL-01` (alur utama: login → pilih mata kuliah → buka topik → unduh materi); `TC-TGS-04` (alur alternatif: koneksi terputus di tengah unggah) |
| Equivalence Partitioning (EP) | Membagi masukan menjadi kelas valid dan tidak valid, lalu cukup satu nilai wakil dari tiap kelas | Unggah PDF valid (`TC-TGS-01`) vs berkas `.exe` (`TC-TGS-05`); login password salah (`TC-LGN-02`) |
| Boundary Value Analysis (BVA) | Menguji nilai tepat di batas, satu di bawah, dan satu di atas | `TC-TGS-02` menguji 5.242.879 byte dan 5.242.880 byte (tepat 5 MB); `TC-TGS-03` menguji batas bawah 0 byte |

Ketiga teknik saling melengkapi: EP dan BVA memeriksa validasi masukan pada satu fungsi, sedangkan UC memeriksa rangkaian langkah yang dialami pengguna sebenarnya.

### 3.4 Alasan Tidak Memakai White Box

White-box memerlukan akses ke struktur internal dan kode program, yang tidak tersedia bagi penguji.

---

## 4. Strategi dan Desain Pengujian

### 4.1 Strategi Pelaksanaan

Urutan pengujian: **smoke test** (login dan dasbor) → **pengujian fungsional** → **pengujian non-fungsional** → **regresi**. Setiap skenario dijalankan secara manual lebih dulu untuk memastikan alurnya benar, kemudian skenario yang stabil (login dan unggah berkas) diotomasikan dengan Selenium agar dapat diulang saat regresi.

### 4.2 Tabel Test Case Fungsional

Prioritas: **T** = Tinggi, **S** = Sedang. Metode: **A** = Otomasi (Selenium), **M** = Manual, **A\*** = Otomasi dengan fallback manual bila CAPTCHA menghalangi.

| ID | Fitur | Skenario | Teknik | Langkah / Input | Hasil yang Diharapkan | Prior. | Metode |
|---|---|---|---|---|---|---|---|
| TC-LGN-01 | Login | Login dengan kredensial valid | UC, EP | Buka `sunan.umk.ac.id`, buka halaman login, isi username dan password akun mahasiswa uji yang valid, lalu klik **Masuk**. | Login berhasil dan pengguna diarahkan ke dasbor yang memuat daftar mata kuliahnya. | T | A* |
| TC-LGN-02 | Login | Login dengan kredensial tidak valid | EP | Isi username valid dengan password salah pada halaman login, lalu klik **Masuk**. | Login ditolak, pesan kesalahan tampil, pengguna tetap di halaman login, dan pesan tidak menyebut isian yang salah. | T | A* |
| TC-MKL-01 | Mata Kuliah | Membuka mata kuliah dan mengunduh materi | UC | Login sebagai mahasiswa uji, klik satu mata kuliah, buka salah satu topiknya, lalu unduh satu berkas materi. | Halaman mata kuliah dan materi tampil lengkap, berkas terunduh utuh dan dapat dibuka. | T | M |
| TC-TGS-01 | Tugas | Unggah tugas format PDF valid | EP | Buka tugas pada mata kuliah uji, unggah PDF sebelum tenggat, lalu simpan perubahan. | Berkas diterima, status berubah menjadi terkumpul, dan nama berkas tampil. | T | A |
| TC-TGS-02 | Tugas | Ukuran di bawah dan tepat pada batas | BVA | Unggah (terpisah) PDF 5.242.879 byte, lalu PDF 5.242.880 byte (tepat 5 MB). | Kedua berkas diterima tanpa pesan galat. Batas 5 MB mengacu BR-01 Test Plan dan perlu dicocokkan dengan perilaku sistem. | S | A |
| TC-TGS-03 | Tugas | Berkas kosong (0 byte) | BVA, EP | Unggah berkas 0 byte (`berkas_0_byte.bin`) melalui *File picker*. | Berkas ditolak dengan pesan yang jelas dan status pengumpulan tidak berubah. | S | A |
| TC-TGS-04 | Tugas | Koneksi terputus saat unggah | UC | Mulai mengunggah berkas, matikan Wi-Fi di tengah proses, lalu sambungkan kembali. | Galat unggah tampil, tidak ada pengumpulan setengah jadi yang tersimpan, dan pengguna dapat mengunggah ulang. | T | M |
| TC-TGS-05 | Tugas | Format tidak diizinkan | EP | Unggah berkas tiruan tidak berbahaya berekstensi `.exe` (tipe diizinkan: doc, docx, pdf, rtf). | Berkas ditolak dengan pesan bahwa format tidak didukung. | T | A |
| TC-TGS-06 | Tugas | Mengirim dua berkas dengan nama yang sama | UC | Pada tugas di mata kuliah uji, unggah satu PDF lewat *File picker > Upload a file*, lalu unggah PDF lain dengan nama yang sama. | Sistem mendeteksi nama yang sama dan meminta keputusan pengguna (timpa, ganti nama, atau batal), tanpa menimpa berkas secara diam-diam. | S | M |
| TC-AKS-01 | Penilaian | Mahasiswa membuka halaman penilaian | UC | Login sebagai mahasiswa uji, lalu buka halaman Grades (*Home > Dashboard > Grades*). | Halaman Grades menampilkan nama mahasiswa dan daftar nilai mata kuliah yang diikutinya sendiri. | T | M |

> **Catatan `TC-TGS-02`.** Batas 5 MB mengacu BR-01 Test Plan. Pada eksekusi diperoleh batas aktual sistem 20 MB dan maksimal 1 berkas, sehingga `TC-TGS-02` perlu diuji ulang pada batas 20 MB (lihat §6.2).

### 4.3 Pengujian Non-Fungsional

| Aspek | Rencana Pengujian | Metode | Hasil Diharapkan |
|---|---|---|---|
| Kinerja | Mengukur waktu muat halaman login, dasbor, dan halaman mata kuliah pada koneksi stabil. | Manual + DevTools | Waktu muat tercatat dan tidak terjadi timeout atau elemen hilang |
| Kompatibilitas | Menjalankan skenario utama (login, unggah tugas) pada Chrome, Firefox, dan Edge. | Manual + Selenium | Tampilan dan alur inti konsisten pada ketiga browser |
| Keamanan dasar | Memeriksa penggunaan HTTPS, serta sesi yang berakhir setelah logout (halaman tidak dapat dibuka kembali lewat tombol Back). | Manual | Situs memakai HTTPS; halaman terproteksi tidak bisa dibuka ulang setelah keluar |
| Keandalan | Mengulang skenario login dan unggah beberapa kali; perilaku koneksi terputus (`TC-TGS-04`) juga menjadi bahan evaluasi keandalan. | Manual | Perilaku konsisten pada pengulangan; tidak ada kegagalan yang berbeda antar percobaan |

> **Catatan.** Ruang lingkup menyatakan fitur logout tidak diuji sebagai fitur. Butir "sesi yang berakhir setelah logout" pada keamanan dasar hanya memeriksa perilaku sesi (apakah halaman terproteksi dapat dibuka kembali), bukan alur logout itu sendiri. Bila butir ini dihapus dari rencana, selisihnya dicatat terhadap dokumen acuan.

### 4.4 Kriteria Lulus/Gagal

- **Lulus:** hasil aktual sama dengan hasil yang diharapkan.
- **Gagal:** hasil aktual berbeda dari hasil yang diharapkan; dicatat sebagai temuan beserta tingkat keparahan.
- **Blocked:** skenario tidak dapat diuji (misalnya CAPTCHA atau kondisi jaringan menghalangi).

**Tingkat keparahan temuan** (alat bantu pelaporan, tidak memengaruhi kriteria lulus di atas):

| Tingkat | Definisi |
|---|---|
| Kritis | Sistem tidak dapat dipakai atau data bocor |
| Major | Fitur utama gagal berfungsi |
| Minor | Fitur sekunder bermasalah |
| Kosmetik | Kesalahan tampilan atau salah ketik |

### 4.5 Format Pencatatan

**Test case:** ID, fitur, skenario, teknik, prasyarat, langkah, data uji, hasil yang diharapkan, hasil aktual, status (lulus/gagal/blocked), dan bukti (screenshot).

**Laporan temuan:** ID, judul, langkah reproduksi, hasil aktual vs hasil yang diharapkan, tingkat keparahan, bukti, dan lingkungan pengujian (browser, OS, tanggal).

---

## 5. Pengujian Otomasi dengan Selenium

### 5.1 Alasan Memilih Otomatisasi

Otomasi lebih cepat, konsisten pada setiap eksekusi, dan cocok untuk pengujian regresi, yaitu memastikan perubahan pada sistem tidak merusak fungsi yang sebelumnya berjalan baik (Sofani & Idris, 2024).

### 5.2 Alat yang Digunakan

Python, Selenium WebDriver, dan pytest sebagai kerangka penjalan test serta pelapor hasil. Otomasi dijalankan pada tiga browser: Chrome (termasuk Chromium dan Brave), Firefox, dan Microsoft Edge. Setiap browser memakai web driver sendiri, yaitu chromedriver, geckodriver, dan msedgedriver.

Struktur proyek otomasi:

```
main.py              titik eksekusi seluruh pengujian
berkas/              berkas uji (PDF valid, batas ukuran, berkas kosong, berkas terlarang)
hasil/               log, tangkapan layar, dan laporan per browser
src/
  konfigurasi.py     pembacaan berkas .env dan daftar browser
  browser.py         pembuatan driver tiap browser
  data_uji.py        pembuat berkas uji
  pelapor.py         log, tangkapan layar, dan laporan
  halaman/           locator dan alur tiap halaman (login, tugas)
  uji/               test case pytest dan panduan skenario manual
```

### 5.3 Pembagian Skenario

| Otomasi (Selenium) | Manual | Alasan |
|---|---|---|
| `TC-LGN-01`, `TC-LGN-02` | — | Alur login stabil dan tinggi frekuensi regresi |
| `TC-TGS-01`, `TC-TGS-02`, `TC-TGS-03`, `TC-TGS-05` | — | Validasi unggah berupa masukan tunggal yang nilainya dapat disimulasikan |
| — | `TC-MKL-01` | Unduhan berkas dan tampilan materi dinilai manual |
| — | `TC-TGS-04` | Gangguan fisik (Wi-Fi diputus) sulit ditiru skrip |
| — | `TC-TGS-06` | Penanganan dialog nama berkas sama bergantung pada *file picker* sistem |
| — | `TC-AKS-01` | Penilaian tampilan daftar nilai bersifat manual |

Skenario otomatis dapat dijalankan berulang pada Chrome, Firefox, dan Edge. Pengulangan ini sekaligus menjadi bukti pengujian kompatibilitas pada §4.3, dan setiap browser menghasilkan laporan terpisah pada folder `hasil/`.

### 5.4 Keterbatasan Otomatisasi

Otomasi terhambat bila halaman memakai CAPTCHA, dan skrip mudah rusak ketika locator elemen berubah akibat pembaruan tampilan. Otomasi juga tidak menilai tampilan secara subjektif (misalnya kejelasan pesan galat) dan sulit meniru gangguan fisik seperti Wi-Fi yang diputus, sehingga skenario tersebut tetap diuji manual.

Pada halaman login Sunan UMK terdapat reCAPTCHA Enterprise dengan centang "bukan robot". Centang tersebut hanya dapat dicentang manusia, sehingga skenario dijalankan dalam mode headed: operator mencocokkan centang di jendela browser, lalu skenario otomatis melanjutkan setelah respons terisi. Bila centang tidak dicentang dalam batas waktu, skenario ditandai terhalang (dilewati), bukan gagal.

---

## 6. Hasil Pelaksanaan

### 6.1 Ringkasan

| Fitur | Jumlah test case | Lulus | Gagal |
|---|---|---|---|
| Login | 2 | 2 | 0 |
| Mata Kuliah | 1 | 1 | 0 |
| Tugas | 6 | 5 | 1 |
| Penilaian | 1 | 1 | 0 |
| **Total** | **10** | **9 (90%)** | **1 (10%)** |

Dari 10 test case, 9 lulus dan 1 gagal (`TC-TGS-04`), sehingga tingkat keberhasilan sebesar 90%. Pengujian non-fungsional pada tahap ini masih berupa rencana (§4.3).

### 6.2 Temuan

- **`TC-TGS-04` (gagal):** saat koneksi dimatikan, *File picker* tidak memuat dan tidak menampilkan pesan galat yang jelas. Dugaan penyebab: kegagalan permintaan jaringan pada antarmuka unggah belum ditangani (tanpa batas waktu dan pesan cadangan).
- **Batas ukuran berkas:** sistem membatasi 20 MB dan maksimal 1 berkas, berbeda dari 5 MB pada BR-01 Test Plan. `TC-TGS-02` perlu diuji ulang terhadap batas 20 MB.
- **Pesan galat:** pesan penolakan berkas kosong dan format tidak diizinkan berbahasa Inggris, dan pesan format tidak menyebut tipe berkas yang diizinkan.
- **Nilai positif (`TC-TGS-06`):** dua berkas bernama sama ditangani dengan dialog *File exists* (Overwrite, Rename, Cancel), sehingga berkas tidak tertimpa tanpa konfirmasi.

### 6.3 Pembahasan

Fitur yang bersifat alur sederhana (login, membuka mata kuliah, melihat nilai) seluruhnya lulus. Kegagalan hanya muncul pada skenario alternatif, yaitu koneksi terputus, yang diturunkan dari teknik Use Case Testing. Ini menunjukkan bahwa pengujian yang hanya memeriksa masukan valid dan tidak valid (EP) belum cukup, karena kelemahan penanganan galat jaringan baru terlihat saat alur yang tidak ideal dicoba. Dampaknya nyata bagi mahasiswa: unggah yang gagal tanpa pesan jelas dapat membuat mahasiswa mengira tugasnya sudah terkirim, terutama menjelang tenggat.

Pada fitur unggah, validasi masukan sudah baik: berkas kosong, format tidak diizinkan, dan nama ganda semuanya ditangani sistem. Kekurangannya ada pada kejelasan pesan (berbahasa Inggris dan tidak menyebut tipe berkas yang diizinkan) serta ketidakselarasan batas ukuran berkas dengan dokumen kebutuhan (20 MB pada sistem, 5 MB pada BR-01). Ketidakselarasan ini bukan galat sistem, tetapi menandakan dokumen kebutuhan perlu diperbarui, sehingga pengujian juga berfungsi sebagai pemeriksa konsistensi spesifikasi.

Perlu dicatat bahwa jumlah test case pada paper ini hanya 10 dan dijalankan pada satu browser, sehingga hasilnya belum dapat digeneralisasi untuk seluruh fitur dan lingkungan.

---

## 7. Kesimpulan dan Saran

### 7.1 Kesimpulan

Pengujian black-box dengan teknik UC, EP, dan BVA terhadap Sunan UMK menghasilkan 10 test case dengan tingkat keberhasilan 90%. Fungsi inti berjalan sesuai spesifikasi, namun penanganan galat saat koneksi terputus perlu diperbaiki. Dengan demikian tujuan menyusun dan melaksanakan pengujian terpenuhi, dengan catatan pengujian non-fungsional baru berupa rencana.

### 7.2 Saran

- Menambahkan pesan galat dan batas waktu pada antarmuka unggah.
- Menyeragamkan bahasa pesan dan menyebut tipe berkas yang diizinkan.
- Menyesuaikan batas ukuran berkas pada BR-01 dengan perilaku sistem (20 MB).
- Melanjutkan pengujian non-fungsional (kinerja, kompatibilitas browser, keamanan dasar, keandalan).
- Memperluas otomasi Selenium ke seluruh test case regresi.

---

## Lampiran A — Traceability ke Dokumen Acuan

| Bagian dokumen acuan | Bagian rencana ini |
|---|---|
| I. Pendahuluan (latar belakang, tujuan, ruang lingkup, manfaat) | §1 |
| II. Kebutuhan Uji Coba (objek uji, data uji, kriteria lulus/gagal) | §1.4, §2, §4.4 |
| III. Analisis Metode Pengujian (black box, UC/EP/BVA) | §3 |
| IV. Strategi dan Desain Pengujian (tabel test case, NFR) | §4.1–§4.3 |
| V. Pengujian Otomasi dengan Selenium (alat, keterbatasan) | §5 |
| VI. Hasil dan Pembahasan (ringkasan, temuan) | §6 |
| VII. Kesimpulan dan Saran | §7 |

---

## Lampiran B — Kandidat Pengujian Lanjutan (di luar cakupan paper)

Test case di bawah ini **tidak termasuk** 10 test case pada dokumen acuan dan tidak memengaruhi hasil 90% di atas. Disimpan sebagai bahan pengembangan lanjutan bila cakupan pengujian diperluas.

| ID | Kategori | Skenario | Catatan |
|---|---|---|---|
| EXT-01 | Login | Username kosong / password kosong | Validasi isian |
| EXT-02 | Login | Username tidak terdaftar | Pastikan pesan tidak membocorkan info akun |
| EXT-03 | Login | Spasi di awal/akhir username | Perilaku trim konsisten |
| EXT-04 | Login | Tekan Enter untuk submit | Setara klik tombol Masuk |
| EXT-05 | Login | Password tidak tersamar | Input bertipe password |
| EXT-06 | Sesi | Akses URL dashboard tanpa login | Diarahkan ke halaman login |
| EXT-07 | Sesi | Tombol Back setelah keluar | Halaman terproteksi tidak dapat dibuka |
| EXT-08 | Sesi | Timeout setelah idle | Diminta login ulang |
| EXT-09 | Tugas | Unggah setelah tenggat | Ditolak atau ditandai terlambat |
| EXT-10 | Tugas | Kirim ulang / ganti berkas terkumpul | Sesuai kebijakan sistem |
| EXT-11 | Tugas | Unggah pada batas aktual 20 MB | Uji ulang `TC-TGS-02` pada batas sistem |
| EXT-12 | Tugas | Unggah lebih dari 1 berkas | Sistem membatasi maksimal 1 berkas |
| EXT-13 | Materi | Tautan materi rusak (404) | Tidak ada link mati |
| EXT-14 | Keamanan | Atribut cookie sesi Secure/HttpOnly | Pemeriksaan tambahan, perlu izin |
| EXT-15 | Keamanan | Pesan galat membocorkan detail teknis | Pemeriksaan tambahan, perlu izin |
| EXT-16 | NFR | Tampilan responsif HP/tablet/desktop | Pemeriksaan manual |
| EXT-17 | NFR | Konsistensi bahasa pesan dan navigasi keyboard | Pemeriksaan manual |
