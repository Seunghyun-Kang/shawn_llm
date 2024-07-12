import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

class ImageCaptioner:
    def __init__(self, model_name="Salesforce/blip-image-captioning-large"):
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)
        self.processor = BlipProcessor.from_pretrained(model_name)
    
    def generate_caption(self, image_path):
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(image, return_tensors="pt")

        # Generate the caption
        with torch.no_grad():
            outputs = self.model.generate(**inputs)
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)

        return caption

image_path = "bot.jpg"  
captioner = ImageCaptioner()
caption = captioner.generate_caption(image_path)
print(f"Generated Caption: {caption}")
