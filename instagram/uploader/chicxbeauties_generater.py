import os
import sys
import random
import re
from datetime import datetime
from uploader import InstagramUploader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import account_info as account_info

class ImageSelector:
    def __init__(self, folder_path):
        self.folder_path = folder_path
    
    def get_image_paths(self):
        subfolders = self.get_subfolders()
        images = []

        for subfolder in subfolders:
            image_files = self.get_image_files(subfolder)
            image_files = self.filter_images(image_files)
            
            if len(image_files) <= 3:
                selected_images = image_files
            else:
                selected_images = random.sample(image_files, random.randint(2, 3))
            
            images.extend(selected_images)
            
            if len(images) >= 2:
                break
        
        return images

    def get_subfolders(self):
        subfolders = [
            f.path for f in os.scandir(self.folder_path) 
            if f.is_dir() and re.match(r'random_caption_\d+', f.name)
        ]
        subfolders.sort(key=lambda x: int(x.split('_')[-1]))
        return subfolders

    def get_image_files(self, subfolder):
        return [os.path.join(subfolder, f) for f in os.listdir(subfolder) if os.path.isfile(os.path.join(subfolder, f))]

    def filter_images(self, image_files):
        return [f for f in image_files if 'used' not in f]
    
    def rename_images(self, images):
        current_date = datetime.now().strftime("%Y%m%d")
        renamed_images = []
        
        for image in images:
            dir_name, file_name = os.path.split(image)
            name, ext = os.path.splitext(file_name)
            new_name = f"{name}_used_{current_date}{ext}"
            new_path = os.path.join(dir_name, new_name)
            os.rename(image, new_path)
            renamed_images.append(new_path)
        
        return renamed_images
    
    def pick_random_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        chosen_line = random.choice(lines).strip()
        # filtered_caption = self.filter_bmp_characters(chosen_line)
        return chosen_line, lines

    def filter_bmp_characters(self, text):
        # BMP 문자 범위 내의 문자만 허용
        return ''.join(c for c in text if ord(c) <= 0xFFFF)

    def update_caption_file(self, filepath, used_caption, lines):
        with open(filepath, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.strip() != used_caption:
                    file.write(line)

folder_path = "D:\\shawnlab"
caption_file = "C:\\shawn_llm\\instagram\\uploader\\chicxbeauties_caption.txt"

selector = ImageSelector(folder_path)
images = selector.get_image_paths()
caption, captions = selector.pick_random_from_file(caption_file)

uploader = InstagramUploader(account_info.INSTAGRAM_USERNAME4, account_info.INSTAGRAM_PASSWORD4)
uploader.login_instagram()

completed = uploader.upload(images, caption)

if completed == True: 
    selector.rename_images(images)
    selector.update_caption_file(caption_file, caption, captions)
