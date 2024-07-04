import logging
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
import requests
import account_info as account_info
import random
from selenium_stealth import stealth
from selenium.webdriver.common.proxy import Proxy, ProxyType

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramCrawler:
    def __init__(self, username, password, targets):
        self.username = username
        self.password = password
        self.targets = targets
        self.driver = self.initialize_driver()

    def random_sleep(self, min_time=5, max_time=10):
        time.sleep(random.uniform(min_time, max_time))

    def initialize_driver(self):
        logging.info("Initializing the Chrome driver.")
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("log-level=3")  # INFO 및 WARNING 레벨만 표시
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
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

    def login_instagram(self):
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
            # 로그인 후 Instagram 로고가 보일 때까지 대기
            time.sleep(5)
            logging.info("Logged in to Instagram.")
        except Exception as e:
            logging.error(f"Error during login: {e}")
            self.driver.save_screenshot("login_error.png")
            # "Dismiss" 버튼 클릭 시도
            try:
                dismiss_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Dismiss"]'))
                )
                dismiss_button.click()
                logging.info("Clicked 'Dismiss' button")
                self.random_sleep()  # 잠시 대기 후 다시 시도
                self.login_instagram()  # 로그인 재시도
            except Exception as inner_e:
                logging.error(f"Error clicking 'Dismiss' button: {inner_e}")
                self.driver.quit()

    def fetch_all_post_links(self, account, download_folder):
        self.target = account
        logging.info(f"Fetching post links from the account: {account}")
        self.driver.get(f"https://www.instagram.com/{account}/")
        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        except Exception as e:
            logging.error(f"Error loading account page: {e}")
            self.driver.save_screenshot("account_page_error.png")
            return set()
        
        post_links = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        actions = ActionChains(self.driver)

        while True:
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                post_url = link.get_attribute('href')
                if "/p/" in post_url:
                    shortcode = post_url.split("/")[-2]
                    img_filename = os.path.join(download_folder, f'{shortcode}.jpg')
                    if not os.path.exists(img_filename):
                        post_links.add(post_url)

            # 스크롤을 내리는 동작을 추가
            actions.send_keys(Keys.END).perform()
            self.random_sleep()  # 페이지가 로드될 시간을 충분히 주기 위해 잠시 대기

            # "다음" 또는 "더보기" 버튼 클릭
            try:
                load_more_button = self.driver.find_element(By.XPATH, f'//button//span[contains(text(), "{account}")]')
                if load_more_button:
                    load_more_button.click()
                    logging.info(f"Clicked 'Load More' button for account: {account}")
                    time.sleep(3)  # 버튼 클릭 후 로드될 시간을 충분히 주기 위해 잠시 대기
            except Exception:
                pass

            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # 새 링크가 추가되지 않으면 종료
            if new_height == last_height:
                break
            last_height = new_height

        logging.info(f"Collected {len(post_links)} post links.")
        return post_links

    def fetch_image_links(self, post_links):
        image_links = []
        for post_link in post_links:
            # self.logout_instagram()
            self.random_sleep(5, 10)  # 로그아웃 후 대기 시간
            # self.login_instagram()

            self.driver.get(post_link)
            self.random_sleep()  # 인스타 속이기 용

            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
                self.random_sleep()  # 인스타 속이기 용
            except Exception as e:
                logging.warning(f"Timeout waiting for images in post: {post_link}")
                continue

            while True:
                try:
                    images = self.driver.find_elements(By.TAG_NAME, 'img')
                    photo_by_images_url = [image.get_attribute('src') or image.get_attribute('data-srcset')
                                           for image in images if image.get_attribute('alt') and
                                           ("Photo by" or "Photo shared") in image.get_attribute('alt')]
                    image_found = False
                    for url in photo_by_images_url:
                        if url:
                            image_links.append((post_link, url))
                            logging.info(f"Added link num: {len(image_links)}")
                            image_found = True

                    if not image_found:
                        logging.info(f"No images in post: {post_link}")
                        break

                    # "다음" 버튼을 클릭하여 다음 이미지로 이동
                    try:
                        next_button = self.driver.find_element(By.XPATH, '//button[@aria-label="다음" or @aria-label="Next" or @aria-label="next"]')
                        self.driver.execute_script("arguments[0].click();", next_button)  # JavaScript를 사용하여 클릭
                        time.sleep(2)  # 페이지가 로드될 시간을 주기 위해 잠시 대기
                    except Exception as e:
                        break

                except Exception as e:
                    logging.warning(f"Error processing post: {post_link} - {e}")
                    self.driver.save_screenshot("Error processing.png")
                    # "Dismiss" 버튼 클릭 시도
                    try:
                        dismiss_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Dismiss"]'))
                        )
                        dismiss_button.click()
                        logging.info("Clicked 'Dismiss' button")
                    except Exception as inner_e:
                        logging.error(f"Error clicking 'Dismiss' button: {inner_e}")
                        self.driver.quit()
                    break

        logging.info(f"Collected {len(image_links)} image links.")
        return image_links

    def save_post_links(self, post_links, download_folder):
        links_file_path = os.path.join(download_folder, 'post_links.txt')
        with open(links_file_path, 'w', encoding='utf-8') as file:
            for link in post_links:
                file.write(f"{link}\n")
        logging.info(f"Saved post links to {links_file_path}")

    def download_images(self, image_links, download_folder):
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        logging.info("Starting to download images.")

        for post_link, url in image_links:
            shortcode = post_link.split("/")[-2]
            img_filename = os.path.join(download_folder, f'{shortcode}_{image_links.index((post_link, url))}.jpg')

            if not os.path.exists(img_filename):
                img_data = requests.get(url).content
                with open(img_filename, 'wb') as handler:
                    handler.write(img_data)
                logging.info(f"Downloaded {img_filename}")
            else:
                logging.info(f"Image {img_filename} already exists. Skipping download.")

    def logout_instagram(self):
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
            try:
                dismiss_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and @aria-label="Dismiss"]'))
                )
                dismiss_button.click()
                logging.info("Clicked 'Dismiss' button")
            except Exception as inner_e:
                logging.error(f"Error clicking 'Dismiss' button: {inner_e}")
                self.driver.quit()

    def crawl_targets(self):
        self.login_instagram()

        for target_account in self.targets:
            download_folder = 'images'
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)
            post_links = self.fetch_all_post_links(target_account, download_folder)
            self.save_post_links(post_links, download_folder)
            image_links = self.fetch_image_links(post_links)
            self.download_images(image_links, download_folder)

        self.driver.quit()

def main():
    crawler = InstagramCrawler(account_info.INSTAGRAM_USERNAME1, account_info.INSTAGRAM_PASSWORD1, account_info.CRAWLING_TARGET)
    crawler.crawl_targets()

if __name__ == "__main__":
    main()
