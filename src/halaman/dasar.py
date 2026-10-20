# Pencarian elemen dengan beberapa selector kandidat.

from __future__ import annotations

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SELECTOR_CAPTCHA = ".g-recaptcha, iframe[src*='recaptcha'], #g-recaptcha-response"
PESAN_CAPTCHA_KUOTA = ("quota", "too many requests", "recaptcha error", "unusual traffic")


class ElemenTidakDitemukan(Exception):
    # Dilempar saat seluruh selector kandidat gagal cocok.
    pass


def cari_pertama(driver, kandidat: list[tuple[str, str]], batas: int = 10):
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
    isi = teks_halaman(driver)
    for baris in isi.splitlines():
        rendah = baris.lower()
        if any(f.lower() in rendah for f in frasa):
            return baris.strip()
    return ""


def ada_captcha(driver) -> bool:
    return bool(driver.find_elements(By.CSS_SELECTOR, SELECTOR_CAPTCHA))


def captcha_terisi(driver) -> bool:
    # Dijawab dua-duanya: medan respons terisi atau centang di iframe sudah diceklis.
    for medan in driver.find_elements(By.ID, "g-recaptcha-response"):
        if (medan.get_attribute("value") or "").strip():
            return True
    return _anchor_tercentang(driver)


def _anchor_tercentang(driver) -> bool:
    # Centang reCAPTCHA ada di dalam iframe, jadi harus dibaca dari dalamnya.
    for bingkai in driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/anchor']"):
        try:
            driver.switch_to.frame(bingkai)
            centang = driver.find_element(By.ID, "recaptcha-anchor")
            if centang.get_attribute("aria-checked") == "true":
                return True
        except (NoSuchElementException, WebDriverException):
            continue
        finally:
            driver.switch_to.default_content()
    return False


def pesan_kuota_captcha(driver) -> str:
    return cari_teks(driver, PESAN_CAPTCHA_KUOTA)


def xpath_teks(frasa: str) -> str:
    # translate() membuat pencocokan teks tidak membedakan huruf besar-kecil.
    huruf_besar = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    huruf_kecil = "abcdefghijklmnopqrstuvwxyz"
    return f"//*[contains(translate(text(), '{huruf_besar}', '{huruf_kecil}'), '{frasa.lower()}')]"
