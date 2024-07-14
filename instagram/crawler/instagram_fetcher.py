import logging
import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class InstagramFetcher:
    def __init__(self, driver, target_account, img_download_folder, txt_download_folder):
        self.driver = driver
        self.target_account = target_account
        self.img_download_folder = img_download_folder
        self.img_download_ftxt_download_folderolder = txt_download_folder

    def random_sleep(self, min_time=5, max_time=10):
        time.sleep(random.uniform(min_time, max_time))

    def fetch_all_post_links(self):
        logging.info(f"Fetching post links from the account: {self.target_account}")
        self.driver.get(f"https://www.instagram.com/{self.target_account}/")
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
                    img_filename = os.path.join(self.img_download_folder, f'{shortcode}.jpg')
                    if not os.path.exists(img_filename):
                        post_links.add(post_url)

            actions.send_keys(Keys.END).perform()
            self.random_sleep()

            try:
                load_more_button = self.driver.find_element(By.XPATH, f'//button//span[contains(text(), "{self.target_account}")]')
                if load_more_button:
                    load_more_button.click()
                    logging.info(f"Clicked 'Load More' button for account: {self.target_account}")
                    time.sleep(3)
            except Exception:
                pass

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        logging.info(f"Collected {len(post_links)} post links.")
        return post_links

    def fetch_image_links(self, post_links):
        image_links = []
        for post_link in post_links:
            photo_by_images_url = []
            self.random_sleep(5, 10)
            self.driver.get(post_link)
            self.random_sleep()

            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
                self.random_sleep()
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
                            image_found = True

                    if not image_found:
                        logging.info(f"No images in post: {post_link}")
                        break

                    try:
                        next_button = self.driver.find_element(By.XPATH, '//button[@aria-label="다음" or @aria-label="Next" or @aria-label="next"]')
                        self.driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(2)
                    except Exception as e:
                        break

                except Exception as e:
                    logging.warning(f"Error processing post: {post_link} - {e}")
                    self.driver.save_screenshot("Error processing.png")
                    self.dismiss_popup()
                    break

        logging.info(f"Collected {len(image_links)} image links.")
        return image_links

    def save_post_links(self, post_links):
        links_file_path = os.path.join(self.txt_download_folder, f'post_links_{self.target_account}.txt')
        with open(links_file_path, 'w', encoding='utf-8') as file:
            for link in post_links:
                file.write(f"{link}\n")
        logging.info(f"Saved post links to {links_file_path}")

    def save_image_links(self, image_links):
        links_file_path = os.path.join(self.txt_download_folder, f'image_links_{self.target_account}.txt')
        with open(links_file_path, 'w', encoding='utf-8') as file:
            for (post_link, img_link) in image_links:
                file.write(f"{img_link}\n")
        logging.info(f"Saved image links to {links_file_path}")

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
