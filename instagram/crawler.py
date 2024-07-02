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
import account_info

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramCrawler:
    def __init__(self, username, password, targets):
        self.username = username
        self.password = password
        self.targets = targets
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        logging.info("Initializing the Chrome driver.")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("log-level=3")  # INFO 및 WARNING 레벨만 표시
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver

    def login_instagram(self):
        logging.info("Navigating to Instagram login page.")
        self.driver.get("https://www.instagram.com/accounts/login/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
        logging.info("Entering login credentials.")
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        # 로그인 후 Instagram 로고가 보일 때까지 대기
        time.sleep(5)
        logging.info("Logged in to Instagram.")

    def fetch_all_post_links(self, account):
        logging.info(f"Fetching post links from the account: {account}")
        self.driver.get(f"https://www.instagram.com/{account}/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        post_links = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        actions = ActionChains(self.driver)

        while True:
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                post_url = link.get_attribute('href')
                if "/p/" in post_url:
                    post_links.add(post_url)

            # 스크롤을 내리는 동작을 추가
            actions.send_keys(Keys.END).perform()
            time.sleep(1)  # 페이지가 로드될 시간을 충분히 주기 위해 잠시 대기

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

    def save_post_links(self, post_links, download_folder):
        links_file_path = os.path.join(download_folder, 'post_links.txt')
        with open(links_file_path, 'w', encoding='utf-8') as file:
            for link in post_links:
                file.write(f"{link}\n")
        logging.info(f"Saved post links to {links_file_path}")

    def download_images_and_texts(self, post_links, download_folder):
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        existing_files = os.listdir(download_folder)
        logging.info("Starting to download images and texts.")

        for post_link in post_links:
            shortcode = post_link.split("/")[-2]
            shortcode_folder = os.path.join(download_folder, shortcode)
            if not os.path.exists(shortcode_folder):
                os.makedirs(shortcode_folder)

            if any(shortcode in filename for filename in existing_files):
                logging.info(f"Skipping {shortcode} - already downloaded.")
                continue

            self.driver.get(post_link)
            
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
                # time.sleep(2)
            except Exception as e:
                logging.warning(f"Timeout waiting for images in post: {post_link}")
                self.logout_instagram()
                # self.crawl_targets(account_info.INSTAGRAM_USERNAME2, account_info.INSTAGRAM_PASSWORD2)  # Need to add change account
                continue
            
            image_index = 0
            while True:
                try:
                    images = self.driver.find_elements(By.TAG_NAME, 'img')
                    image_found = False
                    
                    for i, image in enumerate(images):
                        try:
                            alt_text = image.get_attribute('alt')
                            if alt_text and "Photo by" in alt_text:
                                img_url = image.get_attribute('src') or image.get_attribute('data-srcset')
                                if img_url:
                                    if not img_url.startswith('data:image'):
                                        if not img_url.startswith('http'):
                                            img_url = urljoin(post_link, img_url)
                                        img_data = requests.get(img_url).content
                                        with open(os.path.join(shortcode_folder, f'{shortcode}_{image_index}.jpg'), 'wb') as handler:
                                            handler.write(img_data)
                                        logging.info(f"Downloaded {shortcode}_{image_index}.jpg")
                                        image_index += 1
                                        image_found = True
                                        if image_index > 0:
                                            continue
                                        break
                        except Exception as e:
                            logging.warning(f"Error processing image in post: {post_link} - {e}")
                    
                    if not image_found:
                        logging.info(f"No more images found for post: {post_link}")
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
                    break
            
            # 게시글 텍스트 다운로드
            try:
                post_text_elements = self.driver.find_elements(By.XPATH, '//span[contains(@style, "line-height: 18px;")]')
                if post_text_elements:
                    post_text = post_text_elements[2].text.splitlines()[2]
                    with open(os.path.join(shortcode_folder, f'{shortcode}.txt'), 'w', encoding='utf-8') as text_file:
                        text_file.write(post_text)
                    logging.info(f"Saved text for {shortcode}.txt")
            except Exception as e:
                pass

    def logout_instagram(self):
        logging.info("Logging out of Instagram.")
        self.driver.get("https://www.instagram.com/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@aria-label='Profile']")))
        profile_icon = self.driver.find_element(By.XPATH, "//span[@aria-label='Profile']")
        profile_icon.click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[text()='Log Out']")))
        logout_button = self.driver.find_element(By.XPATH, "//div[text()='Log Out']")
        logout_button.click()
        time.sleep(1)
        logging.info("Logged out of Instagram.")

    def crawl_targets(self):
        self.login_instagram()
        
        for target_account in self.targets:
            download_folder = os.path.join('instagram_images', target_account)
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)
            post_links = self.fetch_all_post_links(target_account)
            self.save_post_links(post_links, download_folder)
            self.download_images_and_texts(post_links, download_folder)
        
        self.driver.quit()

def main():
    crawler = InstagramCrawler(account_info.INSTAGRAM_USERNAME1, account_info.INSTAGRAM_PASSWORD1, account_info.CRAWLING_TARGET)
    crawler.crawl_targets()

if __name__ == "__main__":
    main()
