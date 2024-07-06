
from stable_diffusion_xl import StableDiffusionXL
from aura import ImageUpscaler
from ip_adapter_face import FaceIDGenerator
from datetime import datetime
from PIL import Image

image_url = "base.jpg"
negative_prompt = "low quality, bad quality, strange, blurr,extra head, extra leg, extra hand"
negative_embedding_path = "./negative_embedding/ng_deepnegative_v1_75t.pt"

output_image_path = "./output/generated_image.png"
prompt = "beautiful korean girl, big tits, model, sexy, black hair, black eye, high quality"


# 1. image generator
lora_paths = [
    # './LoRA/real_korean/koreanDollLikeness_v15.safetensors', 
    './LoRA/real_korean/korean.safetensors', 
    # './LoRA/real_korean/realskin.safetensors'
    './LoRA/shadow/casting shadow style v2.safetensors'
    
    ]

controlnet_paths = ["./controlnet/ip-adapter_xl.pth"]
control_images = [Image.open("base.jpg")]

generator = StableDiffusionXL(lora_paths, image_url)
generated_images = generator.generate_images(prompt, negative_prompt, num_images=5)

# 이미지 저장
for i, img in enumerate(generated_images):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    img.save(f"./output/generated_image_{current_time}_{i}.png")

# ////////////////////////////////////////////////////////////////////////
#Upscaler usage

# output_image_path = f"./output/upscaled_{image_url}"

# upscaler = ImageUpscaler()
# image = upscaler.load_image_from_file(image_url)
# upscaled_image = upscaler.upscale_image(image)


# upscaled_image.save(output_image_path)
# print(f"Image saved at {output_image_path}")

#//////////////////////////////////////////////////////////////////////////////
#Adapter usage

# face_model = "jiwon"

# generator = FaceIDGenerator()
# faceid_embeds = generator.get_face_embeddings(face_model)

# prompt = "photo of Asian girl with black eyes, wearing dress at the beach"

# images = generator.generate_images(
#     prompt=prompt, 
#     negative_prompt=negative_prompt, 
#     faceid_embeds=faceid_embeds, 
#     num_samples=4,
#     num_inference_steps=30, 
#     seed=2023
# )

# for i, img in enumerate(images):
#     output_image_path = f"./output/ip_adapter_{i}.jpg"
#     img.save(output_image_path)
#     print(f"Image saved at {output_image_path}")
