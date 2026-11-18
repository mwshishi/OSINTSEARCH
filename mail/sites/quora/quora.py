from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def check_quora_email(email):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Background mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.quora.com/")
        wait = WebDriverWait(driver, 15)

        # Dismiss cookie banner if present
        try:
            consent_btn = driver.find_element(By.XPATH, "//button[contains(., 'Accept')]")
            consent_btn.click()
            time.sleep(1)
        except Exception:
            pass

        # Click "Sign up with email"
        signup_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Sign up with email']")))
        signup_btn.click()

        # Wait for form and fill it
        name_input = wait.until(EC.presence_of_element_located((By.NAME, "profile-name")))
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))

        name_input.clear()
        name_input.send_keys("somefixedusername")
        email_input.clear()
        email_input.send_keys(email)
        email_input.send_keys(Keys.TAB)

        time.sleep(2)  # allow frontend to validate

        # Check for red error message
        try:
            error_div = driver.find_element(
                By.XPATH,
                "//div[contains(@class, 'qu-color--red_error') and contains(text(), 'Account already exists')]"
            )
            if "account already exists" in error_div.text.strip().lower():
                return True
        except Exception:
            pass

        return False

    except Exception:
        return False  # fail safely if Selenium crashes

    finally:
        driver.quit()
