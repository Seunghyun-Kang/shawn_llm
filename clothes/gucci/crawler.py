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


# # 셀레니움 드라이버 설정 (Chrome 기준)
chrome_options = Options()
chrome_options.add_argument("--headless")
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
# # URL로 이동

url = "https://www.gucci.com/kr"
driver.get(url)
time.sleep(5)
url = "https://www.gucci.com/kr/ko/ca/women/ready-to-wear-for-women-c-women-readytowear"
driver.get(url)

# 페이지가 로드될 시간을 충분히 주기
try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[13]/div[2]/div/div/div[2]/div/div/button') or 
            (By.XPATH, '/html/body/div[12]/div[2]/div/div/div[2]/div/div/button') or 
            (By.XPATH, '/html/body/div[14]/div[2]/div/div/div[2]/div/div/button') or 
            (By.XPATH, '/html/body/div[12]/div[2]/div/div/div[2]/div/button'))
    )
    # 버튼 요소들 찾기
    if element:
        element.click()
    else:
        print("NO COOKIE BANNER")
except Exception as e:
    print("Element not found or no buttons available")
    
try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[16]/div[3]/div/div/div/button'))
            
    )
    # 버튼 요소들 찾기
    if element:
        element.click()
    else:
        print("NO SUBSCRIBE BANNER")
except Exception as e:
    print("Element not found or no buttons available")

try:
    load_more_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[4]/div/div[2]/a"))
        )
    driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
    driver.execute_script("arguments[0].click();", load_more_button)
except Exception as e:
    print("No More button, need to check")

time.sleep(10)


last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # 스크롤을 끝까지 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # 페이지 로드 시간을 위해 잠시 대기
    time.sleep(10)
    # 새로운 페이지 높이 계산
    new_height = driver.execute_script("return document.body.scrollHeight")
    # 더 이상 스크롤 할 수 없으면 종료
    if new_height == last_height:
        break
    last_height = new_height


articles = driver.find_elements(By.XPATH, '/html/body/div[4]/div[4]/div/article')

# srcset 값을 저장할 리스트
srcset_values = []
try:
    with open("image_url_list.txt", "r") as file:
        for line in file:
            srcset_values.append(line.strip())
except Exception as e:
    print("No files")

# 각 요소의 srcset 값 가져오기
for i in range(1, len(articles) + 1):
    try:
        element = driver.find_element(By.XPATH, f'/html/body/div[4]/div[4]/div/article[{i}]/a/div[1]/div/picture/source[1]')
        srcset_value = element.get_attribute('srcset')
        if srcset_value in srcset_values:
            pass
        else:
            srcset_values.append(srcset_value)

    except Exception as e:
        pass

with open("image_url_list.txt", "w") as file:
    for item in srcset_values:
        file.write(item + "\n")

print("목록이 파일에 성공적으로 저장되었습니다.")

# 출력 또는 파일 저장 등 필요한 작업 수행
for idx, srcset in enumerate(srcset_values):
    url = 'https://' + srcset[2:]
    print(f"Element {idx + 1} srcset: {url}")
    try:
        pattern = r'/([^/]+)\.jpg'
        match = re.search(pattern, srcset)

        if match:
            file_name = match.group(1)
            driver.get(url)
            time.sleep(3)
            driver.save_screenshot(f'./output_images/{file_name}.jpg')
        else:
            print("이미지 다운로드에 실패했습니다.")
    except Exception as e:
        print(f"최종적으로 URL을 가져오는 데 실패했습니다: {e}")
driver.quit()
