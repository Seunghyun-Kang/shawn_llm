import logging
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import config
from instagram_login import InstagramLogin
from instagram_fetcher import InstagramFetcher
from instagram_downloader import InstagramDownloader

class InstagramCrawler:
    def __init__(self):
        self.username = config.INSTAGRAM_USERNAME
        self.password = config.INSTAGRAM_PASSWORD
        self.targets = config.CRAWLING_TARGETS
        self.driver = self.initialize_driver()

    def random_sleep(self, min_time=5, max_time=10):
        time.sleep(random.uniform(min_time, max_time))

    def initialize_driver(self):
        logging.info("Initializing the Chrome driver.")
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless")
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

    def crawl_targets(self):
        login_manager = InstagramLogin(self.driver, self.username, self.password)
        login_manager.login()

        for target_account in self.targets:
            fetcher = InstagramFetcher(self.driver, target_account, config.BASE_DOWNLOAD_FOLDER, config.BASE_LINK_FOLDER)
            post_links = fetcher.fetch_all_post_links()
            fetcher.save_post_links(post_links)

            image_links = fetcher.fetch_image_links(post_links)
            fetcher.save_image_links(image_links)

            downloader = InstagramDownloader(config.BASE_DOWNLOAD_FOLDER)
            downloader.download_images(image_links)

        login_manager.logout()
        self.driver.quit()

def main():
    crawler = InstagramCrawler()
    crawler.crawl_targets()

if __name__ == "__main__":
    main()
