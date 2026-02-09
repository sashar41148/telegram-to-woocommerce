import os
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

BASE = os.getenv("WP_BASE", "").rstrip("/")
CK = os.getenv("WC_KEY", "")
CS = os.getenv("WC_SECRET", "")
CONTACT = os.getenv("CONTACT_TG", "https://t.me/YourID")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0 Safari/537.36")

HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
}

def get_cookies_via_browser(target_url: str) -> dict:
    """
    صفحه را با مرورگر headless باز می‌کند تا چالش JS رد شود،
    سپس کوکی‌ها را برمی‌گرداند.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=UA)
        page = context.new_page()

        # همین endpoint را باز می‌کنیم؛ اگر challenge باشد خودش حل می‌شود
        page.goto(target_url, wait_until="networkidle", timeout=60000)

        cookies = context.cookies()
        browser.close()

    # تبدیل لیست کوکی‌ها به dict برای requests
    jar = {}
    for c in cookies:
        jar[c["name"]] = c["value"]
    return jar

def main():
    if not BASE or not CK or not CS:
        print("❌ Missing env vars. Check GitHub Secrets.")
        return

    api_url = f"{BASE}/wp-json/wc/v3/products"

    # 1) گرفتن کوکی‌ها با مرورگر
    cookies = get_cookies_via_browser(api_url)
    print("Got cookies:", list(cookies.keys())[:10])

    # 2) درخواست ساخت محصول با همان کوکی‌ها
    payload = {
        "name": "محصول تست (Playwright bypass)",
        "type": "simple",
        "status": "publish",
        "description": f"توضیحات کامل محصول.\n\n📌 جهت استعلام قیمت پیام بدید: {CONTACT}",
        "short_description": f"📌 جهت استعلام قیمت پیام بدید: {CONTACT}",
    }

    r = requests.post(
        api_url,
        json=payload,
        auth=(CK, CS),
        headers=HEADERS,
        cookies=cookies,
        timeout=60,
        allow_redirects=True,
    )

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("Content-Type"))
    print("RESPONSE_HEAD:", (r.text or "")[:600])

if __name__ == "__main__":
    main()
