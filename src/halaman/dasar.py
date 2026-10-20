"""Pencarian elemen yang tahan perubahan tampilan halaman Sunan UMK."""

from __future__ import annotations

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SELECTOR_CAPTCHA = ".g-recaptcha, iframe[src*='recaptcha'], #g-recaptcha-response"
PESAN_CAPTCHA_KUOTA = ("quota", "too many requests", "recaptcha error", "unusual traffic")


class ElemenTidakDitemukan(Exception):
    """Dilempar saat tidak satu pun selector kandidat cocok."""


def cari_pertama(driver, kandidat: list[tuple[str, str]], batas: int = 10):
    """Kembalikan elemen pertama yang ditemukan dari daftar (strategi, selector)."""
    dicoba = []
    for strategi, selector in kandidat:
        dicoba.append(f"{strategi}={selector}")
        try:
            return WebDriverWait(driver, batas).until(
                EC.presence_of_element_located((strategi, selector))
            )
        except (TimeoutException, NoSuchElementException):
            continue
    raise ElemenTidakDitemukan("Elemen tidak ditemukan. Yang dicoba: " + ", ".join(dicoba))


def teks_halaman(driver) -> str:
    return driver.execute_script("return document.body.innerText") or ""


def cari_teks(driver, frasa: tuple[str, ...]) -> str:
    """Kembalikan baris teks halaman yang memuat salah satu frasa."""
    isi = teks_halaman(driver)
    for baris in isi.splitlines():
        rendah = baris.lower()
        if any(f.lower() in rendah for f in frasa):
            return baris.strip()
    return ""


def ada_captcha(driver) -> bool:
    return bool(driver.find_elements(By.CSS_SELECTOR, SELECTOR_CAPTCHA))


def captcha_terisi(driver) -> bool:
    """reCAPTCHA menyimpan jawaban di medan g-recaptcha-response pada halaman induk."""
    medan = driver.find_elements(By.ID, "g-recaptcha-response")
    if not medan:
        return False
    return bool((medan[0].get_attribute("value") or "").strip())


def pesan_kuota_captcha(driver) -> str:
    return cari_teks(driver, PESAN_CAPTCHA_KUOTA)
