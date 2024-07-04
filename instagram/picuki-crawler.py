import logging
import time
import random
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from selenium_stealth import stealth
import account_info as account_info

class PicukiScraper:
    def __init__(self, profile_url, proxy=None):
        self.profile_url = profile_url
        self.proxy = proxy
        self.driver = self.initialize_driver()
        self.post_ids = []

    def initialize_driver(self):
        logging.info("Initializing the Chrome driver.")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("log-level=3")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        
        return driver

    def random_delay(self):
        time.sleep(random.uniform(5, 10))

    def load_profile_page(self):
        logging.info(f"Accessing profile page: {self.profile_url}")
        self.driver.get(self.profile_url)
        logging.info("Waiting for the page to load...")
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'photo')))
            logging.info("Page loaded successfully.")
        except Exception as e:
            logging.error("Failed to load the profile page. You might be blocked.")
            self.driver.quit()
            raise e

    def collect_post_ids(self):
        post_elements = self.driver.find_elements(By.CLASS_NAME, 'photo')
        logging.info(f"Found {len(post_elements)} posts on the profile page.")

        for idx, post in enumerate(post_elements):
            try:
                logging.info(f"Processing post {idx + 1}/{len(post_elements)}")
                link_element = post.find_element(By.TAG_NAME, 'a')
                post_url = link_element.get_attribute('href')
                logging.info(f"Post URL: {post_url}")

                parsed_url = urlparse(post_url)
                media_id = parsed_url.path.split('/')[-1]
                self.post_ids.append(media_id)
                logging.info(f"Post ID: {media_id}")

                logging.info(f"Finished processing post {idx + 1}/{len(post_elements)}")
                self.random_delay()

            except Exception as e:
                logging.error(f"An error occurred while processing post {idx + 1}/{len(post_elements)}: {e}")

        logging.info(f"Collected {len(self.post_ids)} post IDs.")

    def download_images(self):
        os.makedirs('picuki_images', exist_ok=True)

        for media_id in self.post_ids:
            try:
                post_url = f"https://www.picuki.com/media/{media_id}"
                logging.info(f"Accessing post page: {post_url}")
                self.driver.get(post_url)
                self.random_delay()

                post_images = self.driver.find_elements(By.CLASS_NAME, 'item')
                logging.info(f"Found {len(post_images)} images in the post.")

                for img_idx, img in enumerate(post_images):
                    img_url = img.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    logging.info(f"Downloading image {img_idx + 1}/{len(post_images)} from {img_url}")
                    img_data = requests.get(img_url).content
                    with open(f'picuki_images/{media_id}_{img_idx}.jpg', 'wb') as handler:
                        handler.write(img_data)
                    self.random_delay()

                logging.info(f"Finished processing images for post {media_id}")

            except Exception as e:
                logging.error(f"An error occurred while processing images for post {media_id}: {e}")

            self.random_delay()

    def scrape(self):
        try:
            self.load_profile_page()
            self.collect_post_ids()
            self.download_images()
        finally:
            logging.info("Image download completed.")
            self.driver.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = PicukiScraper(profile_url='https://www.picuki.com/profile/eu_nj', proxy="your_proxy:port")
    scraper.scrape()
import logging
import time
import random
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from selenium_stealth import stealth

class PicukiScraper:
    def __init__(self, profile_url, proxy=None):
        self.profile_url = profile_url
        self.proxy = proxy
        self.driver = self.initialize_driver()
        self.post_ids = []

    def initialize_driver(self):
        logging.info("Initializing the Chrome driver.")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("log-level=3")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        
        return driver

    def random_delay(self):
        time.sleep(random.uniform(5, 10))

    def load_profile_page(self):
        logging.info(f"Accessing profile page: {self.profile_url}")
        self.driver.get(self.profile_url)
        logging.info("Waiting for the page to load...")
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'photo')))
            logging.info("Page loaded successfully.")
        except Exception as e:
            logging.error("Failed to load the profile page. You might be blocked.")
            self.driver.quit()
            raise e

    def collect_post_ids(self):
        post_elements = self.driver.find_elements(By.CLASS_NAME, 'photo')
        logging.info(f"Found {len(post_elements)} posts on the profile page.")

        for idx, post in enumerate(post_elements):
            try:
                logging.info(f"Processing post {idx + 1}/{len(post_elements)}")
                link_element = post.find_element(By.TAG_NAME, 'a')
                post_url = link_element.get_attribute('href')
                logging.info(f"Post URL: {post_url}")

                parsed_url = urlparse(post_url)
                media_id = parsed_url.path.split('/')[-1]
                self.post_ids.append(media_id)
                logging.info(f"Post ID: {media_id}")

                logging.info(f"Finished processing post {idx + 1}/{len(post_elements)}")
                self.random_delay()

            except Exception as e:
                logging.error(f"An error occurred while processing post {idx + 1}/{len(post_elements)}: {e}")

        logging.info(f"Collected {len(self.post_ids)} post IDs.")

    def download_images(self):
        os.makedirs('picuki_images', exist_ok=True)

        for media_id in self.post_ids:
            try:
                post_url = f"https://www.picuki.com/media/{media_id}"
                logging.info(f"Accessing post page: {post_url}")
                self.driver.get(post_url)
                self.random_delay()

                post_images = self.driver.find_elements(By.CLASS_NAME, 'item')
                logging.info(f"Found {len(post_images)} images in the post.")

                for img_idx, img in enumerate(post_images):
                    img_url = img.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    logging.info(f"Downloading image {img_idx + 1}/{len(post_images)} from {img_url}")
                    img_data = requests.get(img_url).content
                    with open(f'picuki_images/{media_id}_{img_idx}.jpg', 'wb') as handler:
                        handler.write(img_data)
                    self.random_delay()

                logging.info(f"Finished processing images for post {media_id}")

            except Exception as e:
                logging.error(f"An error occurred while processing images for post {media_id}: {e}")

            self.random_delay()

    def scrape(self):
        try:
            self.load_profile_page()
            self.collect_post_ids()
            self.download_images()
        finally:
            logging.info("Image download completed.")
            self.driver.quit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for target in account_info.CRAWLING_TARGET:
        scraper = PicukiScraper(profile_url=f'https://www.picuki.com/profile/{target}')
    scraper.scrape()
