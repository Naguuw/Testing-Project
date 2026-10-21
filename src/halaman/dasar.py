from __future__ import annotations

import time

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
    # Dilempar pas semua selector kandidat gagal dicocokkan.
    pass


def cari_elemen(
    driver,
    kandidat: list[tuple[str, str]],
    batas: int = 10,
    harus_tampil: bool = False,
):
    # Batas waktu dibagi rata ke semua kandidat supaya kandidat pertama tidak
    # menghabiskan waktu dan kandidat lain tidak kesempatannya.
    akhir = time.monotonic() + batas
    per_kandidat = max(batas / max(len(kandidat), 1), 0.5)
    for strategi, selector in kandidat:
        sisa = akhir - time.monotonic()
        if sisa <= 0:
            break
        try:
            tunggu = WebDriverWait(driver, max(min(per_kandidat, sisa), 0.5))
            if harus_tampil:
                return tunggu.until(EC.visibility_of_element_located((strategi, selector)))
            return tunggu.until(EC.presence_of_element_located((strategi, selector)))
        except (TimeoutException, NoSuchElementException):
            continue
    return None


def teks_halaman(driver) -> str:
    return driver.execute_script("return document.body.innerText") or ""


def cari_teks(driver, frasa: tuple[str, ...]) -> str:
    for baris in teks_halaman(driver).splitlines():
        if any(kata.lower() in baris.lower() for kata in frasa):
            return baris.strip()
    return ""


def ada_captcha(driver) -> bool:
    return bool(driver.find_elements(By.CSS_SELECTOR, SELECTOR_CAPTCHA))


def captcha_terisi(driver) -> bool:
    # Centang dianggap terisi lewat medan respons atau lewat checkbox di iframe.
    for medan in driver.find_elements(By.ID, "g-recaptcha-response"):
        if (medan.get_attribute("value") or "").strip():
            return True
    return _anchor_tercentang(driver)


def _anchor_tercentang(driver) -> bool:
    # Checkbox reCAPTCHA ada di dalam iframe. harus dibaca dari dalam.
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
