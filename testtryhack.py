from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def check_tryhackme_username(username):
    url = f"https://tryhackme.com/p/{username}"

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    print(f"[DEBUG] Loading {url}...")

    try:
        driver.get(url)
        time.sleep(3)  # Allow JS to load

        if "/not-found" in driver.current_url:
            print(f"[DEBUG] Redirected to /not-found → NOT FOUND")
            found = False
        elif "This page doesn’t exist" in driver.page_source:
            print(f"[DEBUG] Message in page → NOT FOUND")
            found = False
        else:
            print(f"[DEBUG] Account seems to exist → FOUND")
            found = True

    except Exception as e:
        print(f"[ERROR] {e}")
        found = False

    finally:
        driver.quit()

    return url, found
# === Check hardcoded username ===
username = "mwshishi"
url, available = check_tryhackme_username(username)
if available:
    print(f"[✓] Available: {username} at {url}")