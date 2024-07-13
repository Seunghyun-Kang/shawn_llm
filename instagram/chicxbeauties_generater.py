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
    
    def pick_random_from_arrays(self, arrays):
    # 배열 중 하나를 랜덤으로 선택
        chosen_array = random.choice(arrays)
        # 선택된 배열에서 다시 하나의 문자열을 랜덤으로 선택
        return chosen_array

folder_path = "D:\\shawnlab"
caption_list =[
"Shining bright today✨",
"Full of beauty and sophistication💕",
"This is what luxury looks like💫",
"The cutest girl in the world👼",
"A perfect blend of elegance and cuteness✨",
"Captivating with luxurious charm!✨",
"Her smile shines today😊",
"Elegantly confident✨",
"Moments filled with loveliness💖",
"Falling for her luxurious beauty✨",
"Elegance in every detail✨",
"Pure charm and grace💕",
"Simply stunning💫",
"Adorable and chic👼",
"Sophisticated beauty at its best✨",
"Timeless elegance✨",
"Radiating beauty and elegance😊",
"Chic and classy✨",
"Elegance that captivates💖",
"Beautifully sophisticated✨",
"Charming and refined✨",
"Exquisite beauty💫",
"Graceful and lovely💖",
"Elegance redefined✨",
"Sophisticated and sweet😊",
"Beautifully elegant✨",
"Charm that enchants💖",
"Pure elegance✨",
"Refined beauty💫",
"Lovely and luxurious✨",
"Effortlessly elegant✨",
"Glamour and grace💕",
"Beauty in simplicity💫",
"Charming and elegant👼",
"Timeless beauty✨",
"Elegance personified✨",
"Radiant and refined😊",
"Classic charm✨",
"Elegant vibes only💖",
"Graceful moments✨",
"Luxuriously lovely💫",
"Chic elegance💖",
"Pure and simple beauty✨",
"Elegantly poised😊",
"Captivating charm✨",
"Sophisticated allure💖",
"Gorgeous and graceful✨",
"Elegant and enchanting💫",
"Simply elegant✨",
"Radiating elegance💖",
"Isn't she shining bright today?✨",
"How does she manage to look so elegant?💕",
"Could she be any more stunning?💫",
"Who’s the cutest girl in the world?👼",
"Isn't this the perfect blend of elegance and cuteness?✨",
"How captivating is her luxurious charm?✨",
"Isn’t her smile just radiant?😊",
"Could she be more elegantly confident?✨",
"Aren't these moments filled with loveliness?💖",
"Isn't her beauty simply luxurious?✨",
"How effortlessly elegant does she look?✨",
"Isn't she the epitome of glamour and grace?💕",
"How beautiful can simplicity get?💫",
"Isn't she charming and elegant?👼",
"Doesn't she have timeless beauty?✨",
"Isn't elegance personified here?✨",
"Isn't she radiantly refined?😊",
"Aren't these classic charm vibes?✨",
"Who else exudes elegant vibes only?💖",
"Aren't these moments just gracefully captured?✨"
]

selector = ImageSelector(folder_path)
images = selector.get_image_paths()
caption = selector.pick_random_from_arrays(caption_list)

uploader = InstagramUploader(account_info.INSTAGRAM_USERNAME4, account_info.INSTAGRAM_PASSWORD4)
uploader.login_instagram()
completed = uploader.upload(images, caption)

if completed == True: 
    selector.rename_images(images)
