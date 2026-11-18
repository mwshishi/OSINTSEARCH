from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# === Setup Chrome WebDriver ===
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Enable if you don't want GUI
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.quora.com/")
    wait = WebDriverWait(driver, 15)

    # === Dismiss cookie/consent if visible ===
    try:
        consent_btn = driver.find_element(By.XPATH, "//button[contains(., 'Accept')]")
        consent_btn.click()
        time.sleep(1)
    except Exception:
        pass  # No cookie popup shown

    # === Click "Sign up with email" ===
    signup_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Sign up with email']")))
    signup_btn.click()

    # === Wait for and fill in the form ===
    name_input = wait.until(EC.presence_of_element_located((By.NAME, "profile-name")))
    email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))

    name_input.clear()
    name_input.send_keys("test")
    email_input.clear()
    email_input.send_keys("ralucamanea02@gmail.com")
    email_input.send_keys(Keys.TAB)

    # === Give Quora time to validate the email ===
    time.sleep(2)

    # === Look for red error message ===
    error_text = ""
    try:
        error_div = driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'qu-color--red_error') and contains(text(), 'Account already exists')]"
        )
        error_text = error_div.text.strip()
    except Exception:
        pass  # No error shown

    # === Decide based on error ===
    if "account already exists" in error_text.lower():
        print("[Quora] Email is already registered.")
    else:
        print("[Quora] Email may be available.")

finally:
    driver.quit()
