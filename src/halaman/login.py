# Halaman login: isi kredensial, CAPTCHA, dan pemeriksaan hasil login.
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    NoSuchWindowException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By

from .dasar import (
    ada_captcha,
    captcha_terisi,
    cari_elemen,
    cari_teks,
    pesan_kuota_captcha,
    xpath_teks,
)

PETUNJUK_GAGAL = (
    "invalid login",
    "login tidak valid",
    "incorrect",
    "password salah",
    "sandi salah",
)
TANDA_SUKSES = ("/my/", "dashboard", "dasbor")
SELECTOR_PESAN = (
    ".alert-danger",
    "[role='alert']",
    ".loginerrors",
    ".alert",
)
TOMBOL_LOGIN = [
    (By.ID, "loginbtn"),
    (By.CSS_SELECTOR, "button[type='submit']"),
    (By.XPATH, xpath_teks("log in")),
    (By.XPATH, xpath_teks("masuk")),
]


@dataclass
class HasilLogin:
    berhasil: bool
    alasan: str
    pesan: str = ""
    masih_di_login: bool = True
    terblokir: bool = False


class HalamanLogin:
    def __init__(self, driver, konfigurasi):
        self.driver = driver
        self.konfigurasi = konfigurasi
        self.log = logging.getLogger("uji")
        self.alasan_terblokir = ""

    def _alamat_login(self) -> str:
        # Beranda hanya punya form di dalam modal, jadi ke halaman login yang menetap.
        url = self.konfigurasi.url
        if urlsplit(url).path in ("", "/"):
            return url.rstrip("/") + "/login/index.php"
        return url

    def _alihkan_jendela(self) -> None:
        # Jendela yang dikontrol bisa tertutup, lalu pindah ke jendela yang tersisa.
        try:
            self.driver.current_window_handle
        except NoSuchWindowException:
            if self.driver.window_handles:
                self.driver.switch_to.window(self.driver.window_handles[-1])

    def _tunggu_terlihat(self, selector: str, batas: int | None = None):
        # Elemen dengan id yang sama bisa ada beberapa, yang dipakai yang terlihat.
        return cari_elemen(
            self.driver,
            [(By.ID, selector)],
            batas=batas or self.konfigurasi.waktu_tunggu,
            harus_tampil=True,
        )

    def buka(self) -> "HalamanLogin":
        # Cookies dibersihkan supaya setiap percobaan login mulai dari form kosong.
        self.driver.delete_all_cookies()
        self.driver.get(self._alamat_login())
        if self._tunggu_terlihat("username") is None:
            raise TimeoutException("Medan username tidak terlihat di halaman login.")
        return self

    def isi_kredensial(self, pengguna: str, sandi: str) -> None:
        for id_median, nilai in (("username", pengguna), ("password", sandi)):
            medan = self._tunggu_terlihat(id_median)
            if medan is None:
                raise TimeoutException(f"Medan {id_median} tidak terlihat di halaman login.")
            try:
                medan.clear()
                medan.send_keys(nilai)
            except (ElementNotInteractableException, WebDriverException):
                # Medan terkunci elemen lain, jadi diisi lewat JS.
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];"
                    "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
                    medan,
                    nilai,
                )

    def ada_captcha(self) -> bool:
        return ada_captcha(self.driver)

    def tunggu_captcha(self) -> bool:
        if not self.ada_captcha():
            return True
        if self.konfigurasi.headless:
            # CAPTCHA tanpa interaksi bisa terisi sendiri.
            if self._tunggu_token(5):
                return True
            self.alasan_terblokir = (
                "halaman login memakai reCAPTCHA, jalankan dengan --headed "
                "lalu cocokkan CAPTCHA manual"
            )
            self.log.warning("%s.", self.alasan_terblokir)
            return False
        self.log.info(
            "Cocokkan reCAPTCHA di jendela browser (maks %d detik).",
            self.konfigurasi.waktu_captcha,
        )
        if self._tunggu_token(self.konfigurasi.waktu_captcha):
            return True
        self.alasan_terblokir = "reCAPTCHA tidak dicentang dalam batas waktu"
        self.log.warning("%s.", self.alasan_terblokir)
        return False

    def _tunggu_token(self, detik: int) -> bool:
        batas = time.monotonic() + detik
        while time.monotonic() < batas:
            try:
                if captcha_terisi(self.driver):
                    return True
            except NoSuchWindowException:
                self.alasan_terblokir = "jendela browser ditutup sebelum CAPTCHA selesai"
                self.log.warning("%s.", self.alasan_terblokir)
                return False
            time.sleep(1)
        return False

    def kirim(self) -> bool:
        tombol = cari_elemen(
            self.driver,
            TOMBOL_LOGIN,
            batas=self.konfigurasi.waktu_tunggu,
            harus_tampil=True,
        )
        if tombol is None:
            return False
        try:
            tombol.click()
            return True
        except (ElementNotInteractableException, NoSuchElementException, WebDriverException):
            return False

    def sudah_masuk(self) -> bool:
        try:
            if any(bagian in (self.driver.current_url or "") for bagian in TANDA_SUKSES):
                return True
            return bool(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']"))
        except NoSuchWindowException:
            self._alihkan_jendela()
            return bool(self.driver.window_handles)

    def coba_login(self, pengguna: str, sandi: str, percobaan_maks: int = 3) -> HasilLogin:
        for percobaan in range(1, percobaan_maks + 1):
            self.isi_kredensial(pengguna, sandi)
            if not self.tunggu_captcha():
                return HasilLogin(
                    berhasil=False,
                    alasan=self.alasan_terblokir or "reCAPTCHA tidak terpecahkan",
                    terblokir=True,
                )
            if not captcha_terisi(self.driver):
                self.log.info("Token captcha hilang, kemungkinan halaman dimuat ulang.")
                continue
            if not self.kirim():
                self.log.info("Tombol Log in tidak ditemukan, dicoba lagi.")
                continue

            hasil = self.cek_hasil()
            if hasil.berhasil or hasil.pesan:
                return hasil
            self.log.info("Login belum berhasil, dicoba lagi (percobaan %d).", percobaan)
        return HasilLogin(berhasil=False, alasan="Login gagal setelah beberapa percobaan")

    def tunggu_login_manual(self, batas_detik: int | None = None) -> bool:
        batas = batas_detik or self.konfigurasi.waktu_login_manual
        self.log.info(
            "Selesaikan login di jendela browser (username, password, dan centang CAPTCHA). "
            "Batas waktu %d detik.",
            batas,
        )
        akhir = time.monotonic() + batas
        while time.monotonic() < akhir:
            if self.sudah_masuk():
                self.log.info("Sesi masuk terdeteksi, skenario dilanjutkan.")
                return True
            time.sleep(1)
        return False

    def simpan_sesi(self, berkas: Path) -> Path:
        # Sesi login disimpan supaya skenario berikutnya tidak perlu captcha lagi.
        data = [
            {
                "name": cookie["name"],
                "value": cookie["value"],
                "path": cookie.get("path", "/"),
                "domain": cookie["domain"],
                "secure": cookie.get("secure", False),
            }
            for cookie in self.driver.get_cookies()
        ]
        berkas.parent.mkdir(parents=True, exist_ok=True)
        berkas.write_text(json.dumps(data, indent=1), encoding="utf-8")
        return berkas

    def pulihkan_sesi(self, berkas: Path) -> bool:
        if not berkas.exists():
            return False
        try:
            data = json.loads(berkas.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        try:
            # Cookie harus dipasang dari halaman dengan domain yang sama.
            self.driver.get(self.konfigurasi.url)
            for cookie in data:
                self.driver.add_cookie(cookie)
            self.driver.get(self._alamat_login())
        except WebDriverException:
            return False
        # Halaman login yang diteruskan ke dasbor berarti sesi masih hidup.
        return not self.driver.find_elements(By.ID, "loginbtn")

    def pesan_gagal(self) -> str:
        for selector in SELECTOR_PESAN:
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                teks = (elemen.text or "").strip()
                if teks:
                    return teks
        return cari_teks(self.driver, PETUNJUK_GAGAL)

    def cek_hasil(self) -> HasilLogin:
        if self.sudah_masuk():
            return HasilLogin(berhasil=True, alasan="Masuk ke dasbor", masih_di_login=False)

        kuota = pesan_kuota_captcha(self.driver)
        if kuota:
            return HasilLogin(
                berhasil=False,
                alasan="reCAPTCHA tidak dapat dipakai",
                pesan=kuota,
                terblokir=True,
            )

        pesan = self.pesan_gagal()
        if pesan:
            return HasilLogin(berhasil=False, alasan="Login ditolak", pesan=pesan)
        return HasilLogin(
            berhasil=False,
            alasan="Halaman tidak menunjukkan tanda masuk berhasil",
            pesan=pesan,
        )
