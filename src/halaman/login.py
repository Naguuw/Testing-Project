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
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .dasar import ada_captcha, captcha_terisi, cari_teks, pesan_kuota_captcha, xpath_teks

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

    def _alamat_login(self) -> str:
        # Beranda hanya punya form di modal, jadi selalu ke halaman login yang menetap.
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

    def _tunggu_tombol(self, batas: int | None = None) -> bool:
        # Tombol Log in hilang sebentar saat halaman dirender ulang.
        batas = batas or self.konfigurasi.waktu_tunggu
        akhir = time.monotonic() + batas
        while time.monotonic() < akhir:
            for strategi, selector in TOMBOL_LOGIN:
                try:
                    if self.driver.find_element(strategi, selector).is_displayed():
                        return True
                except (NoSuchElementException, WebDriverException):
                    continue
            time.sleep(0.5)
        return False

    def buka(self) -> "HalamanLogin":
        # Cookies dibersihkan supaya setiap percobaan login mulai dari form kosong.
        self.driver.delete_all_cookies()
        self.driver.get(self._alamat_login())
        # Form siap dipakai kalau username terlihat dan tombol submit sudah ada.
        WebDriverWait(self.driver, self.konfigurasi.waktu_tunggu).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        self._tunggu_tombol()
        return self

    def isi_kredensial(self, pengguna: str, sandi: str) -> None:
        # Menunggu medan siap diklik, tidak sekadar ada di halaman.
        tunggu = WebDriverWait(self.driver, self.konfigurasi.waktu_tunggu)
        tunggu.until(EC.element_to_be_clickable((By.ID, "username")))
        tunggu.until(EC.element_to_be_clickable((By.ID, "password")))

        medan = self.driver.find_element(By.ID, "username")
        medan.clear()
        medan.send_keys(pengguna)
        medan_sandi = self.driver.find_element(By.ID, "password")
        medan_sandi.clear()
        medan_sandi.send_keys(sandi)

    def ada_captcha(self) -> bool:
        return ada_captcha(self.driver)

    def tunggu_captcha(self) -> bool:
        # Tunggu centang CAPTCHA, dicentang manusia di mode headed.
        if not self.ada_captcha():
            return True
        if self.konfigurasi.headless:
            self.log.warning(
                "Halaman login memakai reCAPTCHA. Jalankan dengan --headed "
                "lalu cocokkan CAPTCHA manual."
            )
            return False
        self.log.info(
            "Cocokkan reCAPTCHA di jendela browser (maks %d detik).",
            self.konfigurasi.waktu_captcha,
        )
        batas = time.monotonic() + self.konfigurasi.waktu_captcha
        while time.monotonic() < batas:
            try:
                if captcha_terisi(self.driver):
                    return True
            except NoSuchWindowException:
                self.log.warning("Jendela browser ditutup sebelum CAPTCHA selesai.")
                return False
            time.sleep(1)
        self.log.warning("reCAPTCHA tidak dicentang dalam batas waktu.")
        return False

    def kirim(self) -> bool:
        # Tombol Log in dicari dulu karena bisa hilang sebentar saat halaman dirender ulang.
        if not self._tunggu_tombol():
            return False
        for strategi, selector in TOMBOL_LOGIN:
            try:
                self.driver.find_element(strategi, selector).click()
                return True
            except (NoSuchElementException, ElementNotInteractableException, WebDriverException):
                continue
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
        # Isi form, tunggu captcha, lalu klik. Ulangi kalau captcha atau tombol hilang.
        for percobaan in range(1, percobaan_maks + 1):
            self.isi_kredensial(pengguna, sandi)
            if not self.tunggu_captcha():
                return HasilLogin(
                    berhasil=False,
                    alasan="reCAPTCHA tidak dicentang dalam batas waktu",
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
        # Yang login adalah operator di jendela browser.
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
                "name": kuki["name"],
                "value": kuki["value"],
                "path": kuki.get("path", "/"),
                "domain": kuki["domain"],
                "secure": kuki.get("secure", False),
            }
            for kuki in self.driver.get_cookies()
        ]
        berkas.parent.mkdir(parents=True, exist_ok=True)
        berkas.write_text(json.dumps(data, indent=1), encoding="utf-8")
        return berkas

    def pulihkan_sesi(self, berkas: Path) -> bool:
        # Cookie sesi dipasang lagi supaya skenario lanjut tanpa login ulang.
        if not berkas.exists():
            return False
        try:
            data = json.loads(berkas.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        try:
            # Cookie harus dipasang dari halaman dengan domain yang sama.
            self.driver.get(self.konfigurasi.url)
            for kuki in data:
                self.driver.add_cookie(kuki)
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
            pesan=cari_teks(self.driver, PETUNJUK_GAGAL),
        )
