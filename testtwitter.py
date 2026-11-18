from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def is_username_available(username):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    url = f"https://x.com/{username}"
    try:
        print(f"[DEBUG] Checking: {url}")
        driver.get(url)
        time.sleep(3)

        page_source = driver.page_source

        if "This account doesn’t exist" in page_source or "Try searching for another" in page_source:
            print(f"[DEBUG] Detected 'account doesn't exist' for {username}")
            driver.quit()
            return True
        else:
            print(f"[DEBUG] Account seems to exist for {username}")
            driver.quit()
            return False

    except Exception as e:
        print(f"[ERROR] {username}: {e}")
        driver.quit()
        return False

# === Check hardcoded username ===
username = "elonmusk"
available = is_username_available(username)

if available:
    print(f"[✓] Available: {username}")
else:
    print(f"[X] Taken: {username}")
