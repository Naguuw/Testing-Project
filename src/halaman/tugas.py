# Halaman tugas: buka file picker, unggah berkas, simpan, dan baca status.

from __future__ import annotations

import time
from pathlib import Path

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .dasar import (
    ElemenTidakDitemukan,
    cari_pertama,
    cari_teks,
    teks_halaman,
    xpath_teks,
)

# Id dari Moodle (yui_..._822) berubah tiap halaman, jadiselector pakai name dan class.
MEDAN_BERKAS = [
    (By.CSS_SELECTOR, "input[name='repo_upload_file']"),
    (By.ID, "file_submission_attachment"),
    (By.CSS_SELECTOR, "input[type='file'][name='attachment']"),
    (By.CSS_SELECTOR, "input[type='file']"),
]
MEDAN_SAVE_AS = [
    (By.CSS_SELECTOR, "input[name='title']"),
]
TOMBOL_UPLOAD_MODAL = [
    (By.CSS_SELECTOR, "button.fp-upload-btn"),
]
PEMICU_FILE_PICKER = [
    (By.CSS_SELECTOR, ".form-control-file button"),
    (By.CSS_SELECTOR, "button.filepicker"),
    (By.CSS_SELECTOR, "a.filepicker"),
    (By.XPATH, xpath_teks("file picker")),
    (By.XPATH, xpath_teks("choose file")),
    (By.XPATH, xpath_teks("pilih berkas")),
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
        "'unggah berkas')]/parent::a",
    ),
]
TOMBOL_SIMPAN = [
    (By.CSS_SELECTOR, "button[name='submitbutton']"),
    (By.CSS_SELECTOR, "input[name='submitbutton']"),
    (By.XPATH, xpath_teks("save changes")),
    (By.XPATH, xpath_teks("simpan perubahan")),
    (By.CSS_SELECTOR, "button[type='submit']"),
]
TOMBOL_KIRIM_FINAL = [
    (By.XPATH, xpath_teks("submit assignment")),
    (By.XPATH, xpath_teks("kirim tugas")),
]
PESAN_TOLAK = (
    "not allowed",
    "file type",
    "format",
    "unsupported",
    "extension",
    "too large",
    "terlalu besar",
    "maximum file size",
    "tidak diizinkan",
    "tidak didukung",
)
STATUS_TERKUMPUL = (
    "submitted for grading",
    "draft submission",
    "terkumpul",
    "telah dikumpulkan",
    "kirim tugas berhasil",
)
STATUS_KOSONG = ("no file submitted", "belum ada berkas", "not submitted")


class HalamanTugas:
    def __init__(self, driver, konfigurasi):
        self.driver = driver
        self.konfigurasi = konfigurasi

    def buka(self, url: str | None = None) -> "HalamanTugas":
        target = url or self.konfigurasi.url_tugas
        if not target:
            raise RuntimeError("URL halaman tugas belum diisi. Set SUNAN_URL_TUGAS di berkas .env.")
        # Tanpa action=editsubmission Moodle hanya menampilkan status, bukan form unggah.
        if "action=" not in target:
            target = f"{target}{'&' if '?' in target else '?'}action=editsubmission"
        self.driver.get(target)
        return self

    def _klik(self, kandidat, batas: int = 8) -> bool:
        try:
            tombol = cari_pertama(self.driver, kandidat, batas=batas)
        except ElemenTidakDitemukan:
            return False
        try:
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

    def _medan_berkas(self):
        return cari_pertama(self.driver, MEDAN_BERKAS, batas=5)

    def _buka_file_picker(self) -> bool:
        # Modal file picker Moodle memuat form upload di dalam dialog.
        if not self._klik(PEMICU_FILE_PICKER):
            return False
        try:
            WebDriverWait(self.driver, self.konfigurasi.waktu_tunggu).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".file-picker"))
            )
        except (TimeoutException, WebDriverException):
            return False
        return True

    def _ke_dalam_frame(self) -> None:
        # Sebagian versi Moodle memuat isi file picker lewat iframe.
        for bingkai in self.driver.find_elements(By.CSS_SELECTOR, "iframe"):
            sumber = bingkai.get_attribute("src") or ""
            if "repository" in sumber or "filepicker" in sumber or "repo" in sumber:
                self.driver.switch_to.frame(bingkai)
                return

    def _pilih_tab_upload(self) -> None:
        self._klik(TAB_UPLOAD, batas=5)
        time.sleep(0.5)

    def _isi_save_as(self, nama: str) -> None:
        try:
            medan = cari_pertama(self.driver, MEDAN_SAVE_AS, batas=5)
        except ElemenTidakDitemukan:
            return
        try:
            medan.clear()
            medan.send_keys(nama)
        except (ElementNotInteractableException, WebDriverException):
            pass

    def unggah(self, berkas: Path) -> str:
        # Jalur langsung: medan file ada di halaman tugas.
        try:
            medan = self._medan_berkas()
        except ElemenTidakDitemukan:
            medan = None
        if medan is not None:
            self._kirim_berkas(medan, berkas)
            return berkas.name

        # Jalur lewat modal File picker: Upload a file -> pilih berkas -> Upload this file.
        if not self._buka_file_picker():
            raise ElemenTidakDitemukan(
                "Medan upload berkas tidak ditemukan dan file picker tidak bisa dibuka."
            )
        self._ke_dalam_frame()
        self._pilih_tab_upload()
        medan = self._medan_berkas()
        self._kirim_berkas(medan, berkas)
        self._isi_save_as(berkas.name)
        self._klik(TOMBOL_UPLOAD_MODAL, batas=10)
        self._tunggu_nama_berkas(berkas.name)
        return berkas.name

    def _tunggu_nama_berkas(self, nama: str, batas: int = 20) -> bool:
        akhir = time.monotonic() + batas
        while time.monotonic() < akhir:
            if nama.lower() in teks_halaman(self.driver).lower():
                return True
            time.sleep(0.5)
        return False

    def nama_berkas_terunggah(self) -> str:
        for selector in (
            ".filename a",
            ".filename",
            ".file-name",
            ".queue .filename",
            "a[href*='pluginfile']",
        ):
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                teks = (elemen.text or "").strip()
                if teks:
                    return teks
        return ""

    def kirim(self) -> bool:
        # Tombol Save changes menyimpan berkas, tombol submit menutup pengiriman.
        if not self._klik(TOMBOL_SIMPAN):
            return False
        self._tunggu_halaman()
        if self._klik(TOMBOL_KIRIM_FINAL):
            self._tunggu_halaman()
        return True

    def _tunggu_halaman(self) -> None:
        try:
            WebDriverWait(self.driver, self.konfigurasi.waktu_tunggu).until(
                EC.staleness_of(self.driver.find_element(By.TAG_NAME, "body"))
            )
        except (TimeoutException, NoSuchElementException, WebDriverException):
            pass

    def pesan_tolak(self) -> str:
        pesan = cari_teks(self.driver, PESAN_TOLAK)
        if pesan:
            return pesan
        for selector in (".alert-danger", ".invalid-feedback", "[role='alert']", ".alert"):
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                teks = (elemen.text or "").strip()
                if teks:
                    return teks
        return ""

    def sudah_terkumpul(self) -> bool:
        isi = teks_halaman(self.driver).lower()
        if any(penanda in isi for penanda in STATUS_TERKUMPUL):
            return True
        return bool(self.nama_berkas_terunggah()) and not any(
            penanda in isi for penanda in STATUS_KOSONG
        )

    def simpan_dom(self, folder: Path) -> Path:
        # Cuplikan DOM disimpan supaya selector bisa dibetulkan tanpa menebak.
        folder.mkdir(parents=True, exist_ok=True)
        bagian = []
        for judul, selector in (
            ("area unggah", ".form-control-file, .filemanager, .submission-form"),
            ("modal file picker", ".file-picker"),
            ("status pengumpulan", ".submissionsection, .submission-info, .alert-info"),
        ):
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                bagian.append(f"### {judul}\n{elemen.get_attribute('outerHTML')}\n")
                break
        for elemen in self.driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .alert, .invalid-feedback"):
            bagian.append(f"### pesan\n{elemen.get_attribute('outerHTML')}\n")
        berkas = folder / "dom_tugas.html"
        berkas.write_text("\n".join(bagian), encoding="utf-8")
        return berkas
