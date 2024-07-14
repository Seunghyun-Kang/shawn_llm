import logging
import os
import requests

class InstagramDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder

    def download_images(self, image_links):
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        logging.info("Starting to download images.")

        i = 0
        for post_link, url in image_links:
            i = i+1
            shortcode = post_link.split("/")[-2]
            img_filename = os.path.join(self.download_folder, f'{shortcode}_{i}.jpg')

            if not os.path.exists(img_filename):
                img_data = requests.get(url).content
                with open(img_filename, 'wb') as handler:
                    handler.write(img_data)
                logging.info(f"Downloaded {img_filename}")
            else:
                logging.info(f"Image {img_filename} already exists. Skipping download.")
