"""Halaman tugas (Modu) Sunan UMK: unggah berkas, kirim, dan baca status pengumpulan."""

from __future__ import annotations

from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .dasar import ElemenTidakDitemukan, cari_pertama, cari_teks, teks_halaman

MEDAN_BERKAS = [
    (By.ID, "file_submission_attachment"),
    (By.CSS_SELECTOR, "input[type='file'][name='attachment']"),
    (By.CSS_SELECTOR, "input[type='file']"),
]
TOMBOL_FILE_PICKER = [
    (By.CSS_SELECTOR, "a[href*='filemanager']"),
    (By.CSS_SELECTOR, ".filepicker a"),
    (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'file picker')]"),
    (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'tambahkan berkas')]"),
    (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add a file')]"),
]
TOMBOL_KIRIM = [
    (By.CSS_SELECTOR, "button[name='submitbutton']"),
    (By.CSS_SELECTOR, "input[name='submitbutton']"),
    (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'kirim tugas')]"),
    (By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit assignment')]"),
    (By.CSS_SELECTOR, "button[type='submit']"),
]
PESAN_TOLAK = (
    "format",
    "tipe berkas",
    "file type",
    "not allowed",
    "tidak diizinkan",
    "tidak didukung",
    "unsupported",
    "extension",
    "too large",
    "terlalu besar",
    "maximum file size",
)
STATUS_TERKUMPUL = ("submitted for grading", "terkumpul", "telah dikumpulkan", "kirim tugas berhasil")


class HalamanTugas:
    def __init__(self, driver, konfigurasi):
        self.driver = driver
        self.konfigurasi = konfigurasi

    def buka(self, url: str | None = None) -> "HalamanTugas":
        target = url or self.konfigurasi.url_tugas
        if not target:
            raise RuntimeError(
                "URL halaman tugas belum diisi. Set SUNAN_URL_TUGAS di berkas .env."
            )
        self.driver.get(target)
        return self

    def _medan_berkas(self):
        try:
            return cari_pertama(self.driver, MEDAN_BERKAS, batas=5)
        except ElemenTidakDitemukan:
            pass
        try:
            tombol = cari_pertama(self.driver, TOMBOL_FILE_PICKER, batas=5)
        except ElemenTidakDitemukan as galat:
            raise ElemenTidakDitemukan(
                "Medan berkas tidak ditemukan dan tombol file picker tidak ditemukan."
            ) from galat
        tombol.click()
        return cari_pertama(self.driver, MEDAN_BERKAS, batas=5)

    def unggah(self, berkas: Path) -> str:
        medan = self._medan_berkas()
        medan.send_keys(str(berkas))
        return berkas.name

    def kirim(self) -> bool:
        try:
            tombol = cari_pertama(self.driver, TOMBOL_KIRIM, batas=8)
        except ElemenTidakDitemukan:
            return False
        tombol.click()
        try:
            WebDriverWait(self.driver, self.konfigurasi.waktu_tunggu).until(
                EC.staleness_of(tombol)
            )
        except TimeoutException:
            pass
        return True

    def nama_berkas_terunggah(self) -> str:
        for selector in (".filename a", ".filename", ".queue .filename"):
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                teks = (elemen.text or "").strip()
                if teks:
                    return teks
        return ""

    def pesan_tolak(self) -> str:
        pesan = cari_teks(self.driver, PESAN_TOLAK)
        if pesan:
            return pesan
        for selector in (".alert-danger", ".invalid-feedback", "[role='alert']"):
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                teks = (elemen.text or "").strip()
                if teks:
                    return teks
        return ""

    def sudah_terkumpul(self) -> bool:
        isi = teks_halaman(self.driver).lower()
        return any(penanda in isi for penanda in STATUS_TERKUMPUL)
