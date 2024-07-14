import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class InstagramLogin:
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    def login(self):
        logging.info("Navigating to Instagram login page.")
        self.driver.get("https://www.instagram.com/accounts/login/")
        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME, 'username')))
            logging.info("Entering login credentials.")
            username_input = self.driver.find_element(By.NAME, 'username')
            password_input = self.driver.find_element(By.NAME, 'password')
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            logging.info("Logged in to Instagram.")
        except Exception as e:
            logging.error(f"Error during login: {e}")
            self.driver.save_screenshot("login_error.png")
            self.dismiss_popup()
            self.login()

    def dismiss_popup(self):
        try:
            dismiss_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Dismiss"]'))
            )
            dismiss_button.click()
            logging.info("Clicked 'Dismiss' button")
        except Exception as inner_e:
            logging.error(f"Error clicking 'Dismiss' button: {inner_e}")
            self.driver.quit()

    def logout(self):
        logging.info("Logging out of Instagram.")
        try:
            self.driver.get("https://www.instagram.com/")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//span[@aria-label='Profile']")))
            profile_icon = self.driver.find_element(By.XPATH, "//span[@aria-label='Profile']")
            profile_icon.click()
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[text()='Log Out']")))
            logout_button = self.driver.find_element(By.XPATH, "//div[text()='Log Out']")
            logout_button.click()
            time.sleep(1)
            logging.info("Logged out of Instagram.")
        except Exception as e:
            logging.warning(f"Error during logout: {e}")
            self.dismiss_popup()
