from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import re
from requests.exceptions import RequestException
import urllib.request

from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc

def fetch_url_with_retry(url, retries=3, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
            return response
        except RequestException as e:
            print(f"Error: {e}. Retrying {attempt + 1}/{retries}...")
            time.sleep(2)  # 재시도 전에 잠시 대기
    raise Exception("Failed to fetch URL after several retries")


chrome_driver_path = ChromeDriverManager().install()
with open(chrome_driver_path, 'r+b') as f:
        content = f.read()
        # cdc_ 문자열을 다른 문자열로 변경
        content = content.replace(b'cdc_', b'dsjfgsdhfdshfsdiojisdjfdsb_')
        f.seek(0)
        f.write(content)
        f.truncate()

# # 셀레니움 드라이버 설정 (Chrome 기준)
options = uc.ChromeOptions()
# chrome_options.add_argument("--headless"))
options.add_argument("start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-infobars')
options.add_argument('--disable-notifications')
options.add_argument('--disable-logging')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-blink-features=BlockCredentialedSubresources")

driver = uc.Chrome(service=Service(chrome_driver_path), options=options)

driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'})
            


prefs = {
    'profile.managed_default_content_settings.javascript': 2
}
options.add_experimental_option('prefs', prefs)
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# # URL로 이동

print(chrome_driver_path)


# url = "https://kr.louisvuitton.com"
# driver.get(url)
# time.sleep(5)
url = "https://kr.louisvuitton.com/eng-e1/women/ready-to-wear/all-ready-to-wear/_/N-to8aw9x"
# url = "https://kr.louisvuitton.com/kor-kr/women/ready-to-wear/coats-and-jackets/_/N-t12kgz5u"

driver.get(url)
time.sleep(10)

try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[1]/div[3]/div[1]/header/div/div/nav[1]/div/div[3]/button'))
            
    )
    # 버튼 요소들 찾기
    if element:
        element.click()
    else:
        print("NO MENU BANNER")
except Exception as e:
    print("Element not found or no buttons available")
time.sleep(5)

try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[1]/div[3]/div[1]/header/div/div/nav[1]/div[2]/div[3]/div/div/div/div[1]/ul/li[4]/div[1]/button'))
            
    )
    # 버튼 요소들 찾기
    if element:
        element.click()
    else:
        print("NO WOMEN BANNER")
except Exception as e:
    print("Element not found or no buttons available")

time.sleep(5)

try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[1]/div[3]/div[1]/header/div/div/nav[1]/div[2]/div[3]/div/div/div/div[1]/ul/li[4]/div[2]/div/div/div/ul/li[7]/div[1]/button'))
            
    )
    # 버튼 요소들 찾기
    if element:
        element.click()
    else:
        print("NO CLOTHES BANNER")
except Exception as e:
    print("Element not found or no buttons available")
time.sleep(5)


try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[1]/div[3]/div[1]/header/div/div/nav[1]/div[2]/div[3]/div/div/div/div[1]/ul/li[4]/div[2]/div/div/div/ul/li[7]/div[2]/div/div/div/ul/li[1]/div/a'))
            
    )
    # 버튼 요소들 찾기
    if element:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
    else:
        print("NO ALL BANNER")
except Exception as e:
    print("Element not found or no buttons available")
time.sleep(5)

# last_height = driver.execute_script("return document.body.scrollHeight")
# while True:
#     try:
#         driver.execute_script("window.scrollTo(20, document.body.scrollHeight);")
#         time.sleep(5)  # 페이지가 로드될 시간을 주기

#         # 새로운 페이지 높이 계산
#         new_height = driver.execute_script("return document.body.scrollHeight")

#         # 버튼이 클릭 가능해질 때까지 기다림
#         try:
#             load_more_button = WebDriverWait(driver, 30).until(
#                 EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/main/div/div[3]/button") or (By.XPATH, "/html/body/div[1]/div/div/main/div/div[3]/div[1]/button"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
#             driver.execute_script("arguments[0].click();", load_more_button)
#         except Exception:
#             load_more_button = None

#         if new_height == last_height and load_more_button is None:
#             break
#         last_height = new_height

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         break
try:
    load_more_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/main/div/div[3]/button") or (By.XPATH, "/html/body/div[1]/div/div/main/div/div[3]/div[1]/button"))
    )
    print("FIND BUTTON")
    print(load_more_button)
    load_more_button.click()
except Exception as e:
    load_more_button = None
    print(e)
time.sleep(30)


articles = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/main/div/div[3]/ul/li')
# srcset 값을 저장할 리스트
srcset_values = []
try:
    with open("image_url_list.txt", "r") as file:
        for line in file:
            srcset_values.append(line.strip())
except Exception as e:
    print("No files")

# 각 요소의 srcset 값 가져오기
print(len(articles))
for i in range(1, len(articles) + 1):
    try:
        element = driver.find_element(By.XPATH, f'/html/body/div[1]/div/div/main/div/div[3]/ul/li[{i}]/div/div[1]/div[2]/div/div[2]/ul/li[1]/div/div/picture/img')
        entire_url = element.get_attribute('srcset')
        print(entire_url)
        srcset_value = entire_url.split(',')[0].split(' ')[0]
        print(srcset_value)
        if srcset_value in srcset_values:
            pass
        else:
            srcset_values.append(srcset_value)

    except Exception as e:
        print(e)

with open("image_url_list.txt", "w") as file:
    for item in srcset_values:
        file.write(item + "\n")

print("목록이 파일에 성공적으로 저장되었습니다.")

# 출력 또는 파일 저장 등 필요한 작업 수행
for idx, srcset in enumerate(srcset_values):
    print(f"Element {idx + 1} srcset: {url}")
    try:
        driver.get(url)
        time.sleep(3)
        driver.save_screenshot(f'./output_images/{file_name}.jpg')
    except Exception as e:
        print(f"최종적으로 URL을 가져오는 데 실패했습니다: {e}")
driver.quit()
