import os
import random
import re
from datetime import datetime
from uploader import InstagramUploader
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

folder_path = "D:\\shawnlab"
selector = ImageSelector(folder_path)
images = selector.get_image_paths()

uploader = InstagramUploader(account_info.INSTAGRAM_USERNAME4, account_info.INSTAGRAM_PASSWORD4)
uploader.login_instagram()
completed = uploader.upload(images)

if completed == True: 
    selector.rename_images(images)
