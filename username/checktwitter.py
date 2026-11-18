from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def check_twitter_username(username):
    url = f"https://x.com/{username}"

    options = Options()
    options.headless = True
    options.add_argument("--headless=new")  # Background mode

    try:
        driver = webdriver.Chrome(options=options)
        print(f"[DEBUG] [Twitter] Checking: {url}")
        driver.get(url)
        time.sleep(3)

        page_source = driver.page_source

        if "This account doesn’t exist" in page_source or "Try searching for another" in page_source:
            print(f"[DEBUG] [Twitter] Message: Account does not exist → NOT FOUND")
            found = False
        else:
            print(f"[DEBUG] [Twitter] Message: Account appears to exist → FOUND")
            found = True

        driver.quit()
        return (url, found)

    except Exception as e:
        print(f"[ERROR] [Twitter] Exception: {e}")
        return (url, False)
    
