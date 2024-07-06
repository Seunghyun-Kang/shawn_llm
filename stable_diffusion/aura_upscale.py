from aura_sr import AuraSR
import requests
from io import BytesIO
from PIL import Image

class ImageUpscaler:
    def __init__(self):
        model_path = "fal-ai/AuraSR"
        self.aura_sr = AuraSR.from_pretrained(model_path)

    def load_image_from_url(self, url):
        response = requests.get(url)
        image_data = BytesIO(response.content)
        return Image.open(image_data)
        
    def load_image_from_file(self, file_path):
        return Image.open(file_path)


    def upscale_image(self, image):
        return self.aura_sr.upscale_4x(image)