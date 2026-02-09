import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("WP_BASE", "").rstrip("/")
CK = os.getenv("WC_KEY", "")
CS = os.getenv("WC_SECRET", "")
CONTACT = os.getenv("CONTACT_TG", "https://t.me/YourID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/121.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
    "Connection": "keep-alive",
}

def extract_infinityfree_test_cookie(html: str):
    """
    از HTML چالش InfinityFree مقدار کوکی __test رو در میاره.
    نمونه داخل صفحه:
    document.cookie="__test=...; max-age=21600; ..."
    """
    m = re.search(r'document\.cookie\s*=\s*"(__test=[^;"]+)', html)
    if not m:
        return None
    # m.group(1) مثل: __test=abc123...
    kv = m.group(1)
    name, value = kv.split("=", 1)
    return name, value

def request_with_if_cookie_retry(method: str, url: str, *, json=None, auth=None):
    s = requests.Session()

    # تلاش اول
    r1 = s.request(method, url, json=json, auth=auth, headers=HEADERS, timeout=60, allow_redirects=True)

    # اگر JSON بود یا خطا/موفقیت واقعی بود، برگردون
    ct = (r1.headers.get("Content-Type") or "").lower()
    if "application/json" in ct:
        return r1

    # اگر HTML بود و چالش InfinityFree داشت، کوکی رو استخراج کن و دوباره بزن
    txt = r1.text or ""
    if "__test" in txt and "This site requires Javascript" in txt:
        cookie = extract_infinityfree_test_cookie(txt)
        if cookie:
            name, value = cookie
            s.cookies.set(name, value, domain=None, path="/")

            # بعضی وقت‌ها InfinityFree روی i=1 حساسه (تو همون HTML هم می‌ذاره)
            retry_url = url
            if "i=1" not in retry_url:
                retry_url += ("&" if "?" in retry_url else "?") + "i=1"

            r2 = s.request(method, retry_url, json=json, auth=auth, headers=HEADERS, timeout=60, allow_redirects=True)
            return r2

    # اگر نه cookie پیدا شد نه JSON، همون پاسخ اول
    return r1

def main():
    if not BASE or not CK or not CS:
        print("❌ Missing env vars. Check GitHub Secrets.")
        return

    url = f"{BASE}/wp-json/wc/v3/products"

    payload = {
        "name": "محصول تست (InfinityFree bypass)",
        "type": "simple",
        "status": "publish",
        "description": f"توضیحات کامل محصول.\n\n📌 جهت استعلام قیمت پیام بدید: {CONTACT}",
        "short_description": f"📌 جهت استعلام قیمت پیام بدید: {CONTACT}",
    }

    r = request_with_if_cookie_retry("POST", url, json=payload, auth=(CK, CS))

    print("STATUS:", r.status_code)
    print("CONTENT-TYPE:", r.headers.get("Content-Type"))
    print("RESPONSE_HEAD:", (r.text or "")[:600])

if __name__ == "__main__":
    main()
