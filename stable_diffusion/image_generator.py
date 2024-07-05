
from stable_diffusion_xl import StableDiffusionXL
from aura import ImageUpscaler
from ip_adapter_face import FaceIDGenerator

image_url = "base.jpg"
negative_prompt = "disfigured, ugly, bad, immature, cartoon, anime, 3d, painting, b&w, extra head, extra legs, extra arms, extra body"

# output_image_path = "./output/generated_image.png"
# prompt = "Make her stand up, big tits, same lighting and high-end camera quality, rim lighting, looking at the camera, ultra quality, sharp focus, tack sharp, dof, film grain, 8K UHD, high detailed skin, high detailed skin, skin pores, like real insta-worthy"


# # 1. image generator
# sd_xl = StableDiffusionXL()
# refined_image = sd_xl.generate_image(prompt, negative_prompt,
#                      num_inference_steps=30, high_noise_frac=0.8)

# 이미지 저장
# refined_image.save(output_image_path)
# print(f"Image saved at {output_image_path}")

# ////////////////////////////////////////////////////////////////////////
# IPAdapterFace 클래스 초기화
# ip_adapter = IPAdapterFace()
# # 이미지 생성
# prompt = "Apply the face to the base image with a smiling expression"
# base_image_path = "./base.jpg"
# face_image_path = "./face.png"
# output_image_path = "./output/output_image.png"

# ip_adapter.generate_image(base_image_path, face_image_path, prompt,
#                           num_inference_steps=30, output_image_path=output_image_path)

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

face_model = "jiwon"

generator = FaceIDGenerator()
faceid_embeds = generator.get_face_embeddings(face_model)

prompt = "photo of Asian girl with black eyes, wearing dress at the beach"

images = generator.generate_images(
    prompt=prompt, 
    negative_prompt=negative_prompt, 
    faceid_embeds=faceid_embeds, 
    num_samples=4,
    num_inference_steps=30, 
    seed=2023
)

for i, img in enumerate(images):
    output_image_path = f"./output/ip_adapter_{i}.jpg"
    img.save(output_image_path)
    print(f"Image saved at {output_image_path}")
