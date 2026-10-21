# Halaman tugas: buka file picker, upload berkas, dan cek hasilnya.
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from selenium.common.exceptions import (
    ElementNotInteractableException,
    WebDriverException,
)
from selenium.webdriver.common.by import By

from .dasar import ElemenTidakDitemukan, cari_elemen, teks_halaman, xpath_teks

# Id dari Moodle (yui_..._822) berubah tiap halaman, jadi selector pakai name dan class.
MEDAN_BERKAS = [
    (By.CSS_SELECTOR, "input[name='repo_upload_file']"),
    (By.ID, "file_submission_attachment"),
    (By.CSS_SELECTOR, "input[type='file'][name='attachment']"),
    (By.CSS_SELECTOR, "input[type='file']"),
]
MEDAN_SAVE_AS = "input[name='title']"
TOMBOL_UPLOAD_MODAL = "button.fp-upload-btn"
# Pemicu dari DOM asli: tombol "Add..." di toolbar file manager tugas.
PEMICU_UPLOAD = [
    (By.XPATH, "//i[contains(@class,'fa-file-o')]/parent::a"),
    (By.XPATH, "//a[@title='Add...']"),
    (By.XPATH, "//a[@title='Tambahkan...']"),
    (By.CSS_SELECTOR, ".fm-empty-container .dndupload-message"),
    (By.CSS_SELECTOR, ".dndupload-message"),
    (By.CSS_SELECTOR, ".fm-empty-container"),
]
TAB_UPLOAD = [
    (
        By.XPATH,
        "//span[contains(@class,'fp-repo-name') and "
        "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
        "'upload a file')]/parent::a",
    ),
    (
        By.XPATH,
        "//span[contains(@class,'fp-repo-name') and "
        "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
        "'upload berkas')]/parent::a",
    ),
]
PESAN_TOLAK = (
    "not allowed",
    "unsupported",
    "extension",
    "too large",
    "terlalu besar",
    "is empty",
    "cannot be uploaded",
    "tidak diizinkan",
    "tidak didukung",
)
# Baris halaman yang selalu ada, jadi tidak boleh dianggap pesan error.
TEKS_BUKAN_ERROR = (
    "accepted file types",
    "maximum file size",
    "document files",
    "pdf document",
    "you can drag and drop",
    "file exists",
    "sudah ada",
)


@dataclass
class HasilUpload:
    # Diterima berarti berkas lolos dari tombol Upload this file.
    diterima: bool
    pesan: str = ""
    nama_terupload: str = ""


class HalamanTugas:
    def __init__(self, driver, konfigurasi):
        self.driver = driver
        self.konfigurasi = konfigurasi

    def buka(self, url: str | None = None) -> "HalamanTugas":
        target = url or self.konfigurasi.url_tugas
        if not target:
            raise RuntimeError("URL halaman tugas belum diisi. Set SUNAN_URL_TUGAS di berkas .env.")
        # Tanpa action=editsubmission Moodle hanya menampilkan status, bukan form upload.
        if "action=" not in target:
            target = f"{target}{'&' if '?' in target else '?'}action=editsubmission"
        self.driver.get(target)
        return self

    def _klik(self, kandidat, batas: int = 8) -> bool:
        tombol = cari_elemen(self.driver, kandidat, batas=batas)
        if tombol is None:
            return False
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol)
            tombol.click()
            return True
        except (ElementNotInteractableException, WebDriverException):
            return False

    def _kirim_berkas(self, medan, berkas: Path) -> None:
        try:
            medan.send_keys(str(berkas))
            return
        except (ElementNotInteractableException, WebDriverException):
            pass
        # Medan upload biasanya disembunyikan oleh gaya halaman, lalu ditembus pakai JS.
        self.driver.execute_script(
            "arguments[0].style.display = 'block';"
            "arguments[0].style.opacity = '1';"
            "arguments[0].style.width = '320px';"
            "arguments[0].style.height = '32px';",
            medan,
        )
        medan.send_keys(str(berkas))

    def _picker_terlihat(self):
        # Halaman tugas punya beberapa file picker, yang dipakai yang terlihat.
        for elemen in self.driver.find_elements(By.CSS_SELECTOR, ".file-picker"):
            if elemen.is_displayed():
                return elemen
        return None

    def _di_dalam(self, wadah, selector: str):
        for elemen in wadah.find_elements(By.CSS_SELECTOR, selector):
            return elemen
        return None

    def _nama_berkas_di_picker(self, picker, nama: str) -> str:
        # Berkas yang berhasil diupload muncul di daftar Recent files.
        awalan = nama[:10].lower()
        for elemen in picker.find_elements(By.CSS_SELECTOR, "a, .filename, .file-name"):
            teks = (elemen.text or "").strip()
            alamat = elemen.get_attribute("href") or ""
            if nama.lower() in alamat.lower():
                return teks or nama
            if teks and awalan in teks.lower():
                return teks
        return ""

    def _tunggu_halaman_siap(self, batas: int = 20) -> None:
        # Modul Moodle dimuat lewat AMD, jadi penangan klik belum tentu terpasang.
        akhir = time.monotonic() + batas
        while time.monotonic() < akhir:
            siap = self.driver.execute_script("return document.readyState === 'complete'")
            ada_pemicu = bool(
                self.driver.find_elements(By.CSS_SELECTOR, ".dndupload-message")
            ) or bool(self.driver.find_elements(By.CSS_SELECTOR, "i.fa-file-o"))
            if siap and ada_pemicu:
                time.sleep(1)
                return
            time.sleep(0.5)

    def _klik_pemicu(self) -> bool:
        # Klik lewat JS dulu karena penangan Moodle terikat di JS dan tombol
        # "Add..." hanya berisi ikon tanpa teks.
        hasil = self.driver.execute_script(
            "var el = document.querySelector('i.fa-file-o');"
            "if (el) { el = el.parentElement; }"
            "if (!el) { el = document.querySelector(\"a[title='Add...']\"); }"
            "if (!el) { el = document.querySelector('.fm-empty-container .dndupload-message'); }"
            "if (el) { el.click(); return true; }"
            "return false;"
        )
        if hasil:
            return True
        for strategi, selector in PEMICU_UPLOAD:
            for elemen in self.driver.find_elements(strategi, selector):
                try:
                    elemen.click()
                    return True
                except (ElementNotInteractableException, WebDriverException):
                    continue
        return False

    def _tunggu_modal(self, detik: int = 15) -> bool:
        batas = time.monotonic() + detik
        while time.monotonic() < batas:
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, ".file-picker"):
                if elemen.is_displayed():
                    return True
            time.sleep(0.5)
        return False

    def _pindah_ke_jendela_baru(self, jendela_awal: list[str]) -> None:
        # File picker kadang terbuka di jendela terpisah.
        baru = [handle for handle in self.driver.window_handles if handle not in jendela_awal]
        if baru:
            self.driver.switch_to.window(baru[-1])

    def _buka_file_picker(self) -> bool:
        # Diklik berkali-kali karena penangan Moodle bisa belum terpasang.
        self._tunggu_halaman_siap()
        jendela_awal = list(self.driver.window_handles)
        for _ in range(5):
            self._klik_pemicu()
            if self._tunggu_modal(3):
                self._pindah_ke_jendela_baru(jendela_awal)
                return True
            time.sleep(1)
        return False

    def _ke_dalam_frame(self) -> None:
        # Sebagian versi Moodle memuat isi file picker lewat iframe.
        for bingkai in self.driver.find_elements(By.CSS_SELECTOR, "iframe"):
            sumber = bingkai.get_attribute("src") or ""
            if "repository" in sumber or "filepicker" in sumber or "repo" in sumber:
                self.driver.switch_to.frame(bingkai)
                return

    def _isi_save_as(self, picker, nama: str) -> None:
        medan = self._di_dalam(picker, MEDAN_SAVE_AS) if picker else None
        if medan is None:
            medan = cari_elemen(self.driver, [(By.CSS_SELECTOR, MEDAN_SAVE_AS)], batas=5)
        if medan is None:
            return
        try:
            medan.clear()
            medan.send_keys(nama)
        except (ElementNotInteractableException, WebDriverException):
            pass

    def upload(self, berkas: Path) -> HasilUpload:
        if not self._buka_file_picker():
            raise ElemenTidakDitemukan("File picker tidak terbuka di halaman tugas.")
        self._ke_dalam_frame()

        picker = self._picker_terlihat()
        if picker is not None:
            self._klik(TAB_UPLOAD, batas=5)
            time.sleep(0.5)
            medan = self._di_dalam(picker, "input[name='repo_upload_file']")
        else:
            medan = cari_elemen(self.driver, MEDAN_BERKAS, batas=5)

        if medan is None:
            raise ElemenTidakDitemukan("Medan Choose File tidak ditemukan di file picker.")

        self._kirim_berkas(medan, berkas)
        self._isi_save_as(picker, berkas.name)

        if picker is not None:
            tombol = self._di_dalam(picker, TOMBOL_UPLOAD_MODAL)
            if tombol is not None:
                try:
                    tombol.click()
                except (ElementNotInteractableException, WebDriverException):
                    pass
        else:
            self._klik([(By.CSS_SELECTOR, TOMBOL_UPLOAD_MODAL)], batas=10)

        return self._tunggu_hasil_upload(berkas.name, picker)

    def _tunggu_hasil_upload(self, nama: str, picker=None, batas: int | None = None) -> HasilUpload:
        # Tombol Upload this file yang menentukan berkas diterima atau ditolak.
        batas = batas or self.konfigurasi.waktu_upload
        akhir = time.monotonic() + batas
        while time.monotonic() < akhir:
            # Dialog File exists lebih dulu, itu bukan penolakan.
            self._tangani_dialog_bentrok()
            pesan = self.pesan_tolak()
            if pesan:
                return HasilUpload(diterima=False, pesan=pesan)
            if picker is not None:
                ditemukan = self._nama_berkas_di_picker(picker, nama)
                if ditemukan:
                    return HasilUpload(diterima=True, nama_terupload=ditemukan)
            terupload = self.nama_berkas_terupload(nama)
            if terupload:
                return HasilUpload(diterima=True, nama_terupload=terupload)
            time.sleep(1)
        return HasilUpload(
            diterima=False,
            pesan="Tidak ada tanda berkas diterima maupun pesan penolakan setelah upload.",
        )

    def nama_berkas_terupload(self, nama: str) -> str:
        # Nama berkas yang tampil dipotong Moodle, jadi yang dicek adalah alamatnya.
        for elemen in self.driver.find_elements(By.CSS_SELECTOR, "a[href]"):
            alamat = elemen.get_attribute("href") or ""
            if nama.lower() in alamat.lower():
                return (elemen.text or "").strip() or nama
        awalan = nama[:10].lower()
        for elemen in self.driver.find_elements(
            By.CSS_SELECTOR, ".filename a, .file-name, .fp-file a, .fnp-attachments a"
        ):
            teks = (elemen.text or "").strip()
            if teks and awalan in teks.lower():
                return teks
        return ""

    def _tangani_dialog_bentrok(self) -> bool:
        # Berkas dengan nama sama memunculkan dialog File exists.
        for tombol in ("overwrite", "timpa", "ganti nama", "rename"):
            elemen = cari_elemen(self.driver, [(By.XPATH, xpath_teks(tombol))], batas=2)
            if elemen is None:
                continue
            try:
                elemen.click()
                return True
            except (ElementNotInteractableException, WebDriverException):
                continue
        return False

    def pesan_tolak(self) -> str:
        # Pesan error Moodle muncul di dalam kotak alert.
        for selector in (".alert-danger", ".invalid-feedback", "[role='alert']"):
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                teks = (elemen.text or "").strip()
                if not teks or any(kata in teks.lower() for kata in TEKS_BUKAN_ERROR):
                    continue
                return teks

        # Kalau tidak ada kotak alert, cari kalimat error di dalam modal.
        isi = ""
        for wadah in self.driver.find_elements(By.CSS_SELECTOR, ".file-picker"):
            isi = wadah.text or ""
        if not isi.strip():
            isi = teks_halaman(self.driver)
        for baris in isi.splitlines():
            rendah = baris.lower()
            if any(kata in rendah for kata in TEKS_BUKAN_ERROR):
                continue
            if any(kata in rendah for kata in PESAN_TOLAK):
                return baris.strip()
        return ""
