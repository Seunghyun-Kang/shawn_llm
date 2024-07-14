import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import account_info


# 계정 정보
INSTAGRAM_USERNAME = account_info.INSTAGRAM_USERNAME1
INSTAGRAM_PASSWORD = account_info.INSTAGRAM_PASSWORD1
CRAWLING_TARGETS = account_info.CRAWLING_TARGET_19

# 저장 경로 설정
BASE_DOWNLOAD_FOLDER = 'D:\\shawnlab\\target_19\\images'
BASE_LINK_FOLDER = 'D:\\shawnlab\\target_19\\links'

# 폴더 생성
os.makedirs(BASE_LINK_FOLDER, exist_ok=True)
os.makedirs(BASE_DOWNLOAD_FOLDER, exist_ok=True)