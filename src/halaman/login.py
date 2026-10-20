"""Halaman login Sunan UMK: isi kredensial, CAPTCHA, dan pemeriksaan hasil login."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .dasar import ada_captcha, captcha_terisi, cari_teks, pesan_kuota_captcha

PETUNJUK_GAGAL = ("invalid login", "login tidak valid", "incorrect", "password salah", "sandi salah")
TANDA_SUKSES = ("/my/", "dashboard", "dasbor")
SELECTOR_PESAN = (
    ".alert-danger",
    "[role='alert']",
    ".loginerrors",
    ".alert",
)


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

    def buka(self) -> "HalamanLogin":
        self.driver.get(self.konfigurasi.url)
        WebDriverWait(self.driver, self.konfigurasi.waktu_tunggu).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        return self

    def isi_kredensial(self, pengguna: str, sandi: str) -> None:
        medan = self.driver.find_element(By.ID, "username")
        medan.clear()
        medan.send_keys(pengguna)
        medan_sandi = self.driver.find_element(By.ID, "password")
        medan_sandi.clear()
        medan_sandi.send_keys(sandi)

    def ada_captcha(self) -> bool:
        return ada_captcha(self.driver)

    def tunggu_captcha(self) -> bool:
        """Tunggu CAPTCHA diisi; di mode headful Orang humaine yang mencocokkan."""
        if not self.ada_captcha():
            return True
        if self.konfigurasi.headless:
            self.log.warning("Halaman login memakai reCAPTCHA. Jalankan dengan --headed lalu cocokkan CAPTCHA manual.")
            return False
        self.log.info("Cocokkan reCAPTCHA di jendela browser (maks %d detik).", self.konfigurasi.waktu_captcha)
        try:
            WebDriverWait(self.driver, self.konfigurasi.waktu_captcha, poll_frequency=1).until(
                lambda d: captcha_terisi(d)
            )
            return True
        except TimeoutException:
            self.log.warning("reCAPTCHA tidak diisi dalam batas waktu.")
            return False

    def kirim(self) -> None:
        self.driver.find_element(By.ID, "loginbtn").click()

    def pesan_gagal(self) -> str:
        for selector in SELECTOR_PESAN:
            for elemen in self.driver.find_elements(By.CSS_SELECTOR, selector):
                teks = (elemen.text or "").strip()
                if teks:
                    return teks
        return cari_teks(self.driver, PETUNJUK_GAGAL)

    def cek_hasil(self) -> HasilLogin:
        if any(bagian in (self.driver.current_url or "") for bagian in TANDA_SUKSES):
            return HasilLogin(berhasil=True, alasan="Masuk ke dasbor", masih_di_login=False)
        if self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']"):
            return HasilLogin(berhasil=True, alasan="Menu keluar tampil", masih_di_login=False)

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
