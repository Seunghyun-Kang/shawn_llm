import logging
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import account_info as account_info
import random
from selenium_stealth import stealth
import pyautogui

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramUploader:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = self.initialize_driver()

    def basic_seeker(self, paths, type='click'):
        for path in paths:
            try:
                # 요소가 클릭 가능해질 때까지 기다림
                if(type == 'click'):
                    element = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, path)))
                else:
                    element = self.driver.find_element(By.XPATH, path)
                if(element):
                    break
            except:
                continue
        return element

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
            self.driver.implicitly_wait(3)

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
                self.login_instagram()  
            except Exception as inner_e:
                logging.error(f"Error clicking 'Dismiss' button: {inner_e}")
                self.driver.quit()

    def upload(self, images):
        upload_btn_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[7]/div/span/div/a/div"
        select_file_xpaths = [
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button",
            "/html/body/div[5]/div[1]/div/div/3/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button"
        ]
        select_multiple_btn_xpaths= [
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[2]/div/button/div",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[2]/div/button/div",
            "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[2]/div/button/div"
        ]
        add_additional_photo_btn_xpaths= [
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[1]/div/div/span/div/div[2]/div/div",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[1]/div/div/span/div/div[2]/div/div",
            "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[1]/div/div/span/div/div[2]/div/div"
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div/div[2]/div/div",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div/div[2]/div/div",
            "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div/div[2]/div/div"
        ]
        next_btn_xpaths = [
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div",
            "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div"
        ]
        text_input_xpaths = [
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div[1]",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div[1]",
            "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div[2]/div/div[1]/div[1]",
        ]
        share_btn_xpaths = [
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div",
            "/html/body/div[5]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div",
        ]

        try:
            logging.info("Logging in to Instagram.")
            self.driver.get(f'https://www.instagram.com/{self.username}/')
            time.sleep(5)

            # 사진 업로드 버튼 
            logging.info("Clicking upload button.")
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, upload_btn_xpath)))
                self.driver.find_element(By.XPATH, upload_btn_xpath).click()
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error clicking upload button: {e}")
                self.driver.quit()
                return

            # 파일 업로드 선택 버튼 
            logging.info("Selecting file upload button.")
            try:
                btn = self.basic_seeker(select_file_xpaths)
                btn.click()
            except Exception as e:
                logging.error(f"Error clicking file upload button: {e}")
                self.driver.quit()
                return

            # 파일 업로드 과정 - 사진 1개
            logging.info("Uploading first image.")
            time.sleep(5)
            pyautogui.write(images[0])
            pyautogui.press('enter')
            time.sleep(5)

            if len(images) > 1:
                logging.info("Uploading additional images.")
                try:
                    btn = self.basic_seeker(select_multiple_btn_xpaths)
                    btn.click()
                except Exception as e:
                    logging.error(f"Error clicking select multiple images button: {e}")
                    self.driver.quit()
                    return

                time.sleep(2)
                for i, image in enumerate(images):
                    if i == 0:
                        continue
                    else:
                        logging.info(f"Uploading image {i+1}.")
                        try:
                            btn = self.basic_seeker(add_additional_photo_btn_xpaths)
                            btn.click()
                            pyautogui.write(image)
                            pyautogui.press('enter')
                        except Exception as e:
                            logging.error(f"Error clicking add additional photo button for image {i+1}: {e}")
                            self.driver.quit()
                            return
                time.sleep(2)
        
            # 사진 등록 화면
            logging.info("Proceeding to the next step.")
            try:
                btn = self.basic_seeker(next_btn_xpaths)
                btn.click()
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error clicking next button after uploading images: {e}")
                self.driver.quit()
                return

            # 보정 설정 화면
            logging.info("Proceeding to the filter step.")
            try:
                btn = self.basic_seeker(next_btn_xpaths)
                btn.click()
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error clicking next button on filter step: {e}")
                self.driver.quit()
                return

            # 게시글 등록 화면
            content_text= ""
            hash_Tags = """#china #chinagirl #korea #korean #chinese #chinesegirl #koreangirl #sexy #beautiful #model #models #kpop #kpop #japan #japangirl #japanese #japanesegirl #jpop #hongkong #taiwan #fashion #beauty #style #idol"""
    # #culture #travel #photography #lifestyle #trend #music #entertainment #glamour #stars #celebrity #makeup #skincare #asia #asianbeauty #asianfashion #popculture #fanbase #influencer #artist #singer #dancer #performance

            logging.info("Adding post content and hashtags.")
            try:
                text_input = self.basic_seeker(text_input_xpaths, 'text_input')
                text_input.send_keys(f'{content_text}\n\n\n' + hash_Tags)
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error adding post content and hashtags: {e}")
                self.driver.quit()
                return

            # 공유 버튼
            logging.info("Clicking share button.")
            try:
                btn = self.basic_seeker(share_btn_xpaths)
                btn.click()
                self.driver.implicitly_wait(2)
                logging.info("Upload completed and browser closed.")
            except Exception as e:
                logging.error(f"Error clicking share button: {e}")
                self.driver.quit()
                return
        
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            self.driver.quit()

        return True

