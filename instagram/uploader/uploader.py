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
import sys
import requests
import pyperclip

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import account_info as account_info
import random
from selenium_stealth import stealth
import pyautogui
import undetected_chromedriver as uc

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstagramUploader:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = self.initialize_driver()
        self.success = False

    def basic_seeker(self, paths, type='click'):
        find = False
        test_path = "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div"
        for path in paths:
            try:
                # 요소가 클릭 가능해질 때까지 기다림
                if(type == 'click' or type == 'next' or type == 'share'):
                    element = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, path)))
                else:
                    element = self.driver.find_element(By.XPATH, path)
                if(element):
                    find = True
                    logging.info("Find path:")
                    logging.info(f"{path}")
                    break
            except:
                continue
        if find == False and type == 'next':
            logging.info("Failed to find next, try to find by text")
            spare_path_list = [
                "//div[@role='button' and text()='Next']",
                "//div[@role='button' and text()='Next']/..",
                "//div[@role='button' and text()='Next']/../..",
            ]
            for path in spare_path_list:
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, path))
                    )
                    if(element):
                        logging.info("Find path:")
                        logging.info(f"{path}")
                        break
                except:
                    continue
        if find == False and type == 'share':
            logging.info("Failed to find share, try to find by text")
            spare_path_list = [
                "//div[@role='button' and text()='Share']",
                "//div[@role='button' and text()='Share']/..",
                "//div[@role='button' and text()='Share']/../..",
            ]
            for path in spare_path_list:
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, path))
                    )
                    if(element):
                        logging.info("Find path:")
                        logging.info(f"{path}")
                        break
                except:
                    continue
        return element

    def random_sleep(self, min_time=5, max_time=10):
        time.sleep(random.uniform(min_time, max_time))

    def initialize_driver(self):
        logging.info("Initializing the Chrome driver.")

        chrome_options = uc.ChromeOptions()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-blink-features=BlockCredentialedSubresources")

        chrome_driver_path = ChromeDriverManager().install()
        with open(chrome_driver_path, 'r+b') as f:
            content = f.read()
            # cdc_ 문자열을 다른 문자열로 변경
            content = content.replace(b'cdc_', b'dsjfgsdhfdshfsdiojisdjfdsb_')
            f.seek(0)
            f.write(content)
            f.truncate()
        driver = uc.Chrome(service=Service(chrome_driver_path), options=chrome_options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'})
        
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
            time.sleep(10)
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

    def logout_instagram(self):
        logging.info("Do logout")
        x_button_xpath = ['/html/body/div[6]/div[1]/div/div[2]/div']
        menu_button_xpath = ['/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[3]/span/div/a/div']
        logout_button_xpath = [
            '/html/body/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[6]/div[2]',
            '/html/body/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[6]/div[1]',
            '/html/body/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[6]/div[1]/div/div/div[1]/div/div',
            '/html/body/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[6]/div[1]/div',
            '/html/body/div[2]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[6]/div[1]/div/div',
            ]
        
        try:
            btn = self.basic_seeker(x_button_xpath)
            btn.click()
            logging.info("Clicked 'X' button")
            self.random_sleep()  # 잠시 대기 후 다시 시도
        except Exception as inner_e:
            logging.error(f"Error clicking 'X' button: {inner_e}")
            self.driver.quit()
        
        try:
            btn = self.basic_seeker(menu_button_xpath)
            btn.click()
            logging.info("Clicked 'Menu' button")
            self.random_sleep()  # 잠시 대기 후 다시 시도
        except Exception as inner_e:
            logging.error(f"Error clicking 'Menu' button: {inner_e}")
            self.driver.quit()

        try:
            btn = self.basic_seeker(logout_button_xpath)
            btn.click()
            logging.info("Clicked 'Logout' button")
            self.random_sleep()  # 잠시 대기 후 다시 시도
            self.driver.implicitly_wait(2)
            self.driver.quit()
        except Exception as inner_e:
            logging.error(f"Error clicking 'Logout' button: {inner_e}")
            self.driver.quit()    

    def upload(self, images, caption):
        logging.info(f"caption: {caption}")
        upload_btn_xpath = "/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[7]/div/span/div/a/div"
        select_file_xpaths = [
            "/html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button",
            "/html/body/div[5]/div[1]/div/div/3/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div/button"
        ]
        next_btn_xpaths = [
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]/div/div",
            "/html/body/div[6]/div[1]/div/div[3]/div/div/div/div/div/div/div/div[1]/div/div/div/div[3]",
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
                time.sleep(5)
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, upload_btn_xpath)))
                self.driver.find_element(By.XPATH, upload_btn_xpath).click()
            except Exception as e:
                logging.error(f"Error clicking upload button: {e}")
                self.logout_instagram()
                return False

            # 파일 업로드 선택 버튼 
            logging.info("Selecting file upload button.")
            try:
                time.sleep(5)
                btn = self.basic_seeker(select_file_xpaths)
                btn.click()
                # file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                # file_paths_string = "\n".join(images)
                # file_input.send_keys(file_paths_string)
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error clicking file upload button: {e}")
                self.driver.quit()
                return False

            # 파일 업로드 과정
            logging.info("Uploading image.")
            time.sleep(5)
            file_paths_str = ' '.join([f'"{path}"' for path in images])
            pyautogui.write(file_paths_str)
            pyautogui.press('enter')
            time.sleep(2)
        
            # 사진 등록 화면
            logging.info("Proceeding to the next step.")
            try:
                time.sleep(5)
                btn = self.basic_seeker(next_btn_xpaths, 'next')
                btn.click()
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error clicking next button after uploading images: {e}")
                self.driver.save_screenshot("next_error.png")
                self.logout_instagram()
                return False

            # 보정 설정 화면
            logging.info("Proceeding to the filter step.")
            try:
                time.sleep(5)
                btn = self.basic_seeker(next_btn_xpaths, 'next')
                btn.click()
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error clicking next button on filter step: {e}")
                self.driver.save_screenshot("next_error.png")
                self.logout_instagram()
                return False

            # 게시글 등록 화면
            hash_Tags = """#china #chinagirl #korea #korean #chinesegirl #koreangirl #sexy #beautiful #model #kpop #japan #japangirl #fashion #beauty #style #idol"""
            logging.info("Adding post content and hashtags.")
            try:
                text_input = self.basic_seeker(text_input_xpaths, 'text_input')
                # text_input.send_keys(f'{caption}\n\n\n' + hash_Tags)
                pyperclip.copy(str(f'{caption}\n\n\n' + hash_Tags)) #복사 
                text_input.send_keys(Keys.CONTROL, 'v')  #붙여넣기 
            except Exception as e:
                self.driver.save_screenshot("text_register_error.png")
                logging.error(f"Error adding post content and hashtags: {e}")
                self.logout_instagram()
                return False

            # 공유 버튼
            logging.info("Clicking share button.")
            try:
                time.sleep(5)
                btn = self.basic_seeker(share_btn_xpaths, 'share')
                btn.click()
                self.driver.implicitly_wait(2)
                logging.info("Upload completed and do logout")
                self.success = True
                time.sleep(10)
            except Exception as e:
                self.driver.save_screenshot("share_error.png")
                logging.error(f"Error clicking share button: {e}")
                self.logout_instagram()
                return False
        
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            self.logout_instagram()
        
        self.logout_instagram()
        return self.success

