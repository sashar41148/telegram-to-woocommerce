import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("WP_BASE", "").rstrip("/")
CK = os.getenv("WC_KEY", "")
CS = os.getenv("WC_SECRET", "")
CONTACT = os.getenv("CONTACT_TG", "https://t.me/zare_41148")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SasharBot/1.0)",
    "Accept": "application/json",
}

def main():
    url = f"{BASE}/wp-json/wc/v3/products"
    payload = {
        "name": "محصول تست از GitHub Actions",
        "type": "simple",
        "status": "publish",
        "description": f"توضیحات کامل محصول.\n\n📌 جهت استعلام قیمت پیام بدید: {CONTACT}",
        "short_description": f"📌 جهت استعلام قیمت پیام بدید: {CONTACT}",
    }

    r = requests.post(url, json=payload, auth=(CK, CS), headers=HEADERS, timeout=60)
    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text[:800])

if __name__ == "__main__":
    main()
