# main.py
from ip_adapter_face import IPAdapterFace
# from stable_diffusion_xl import StableDiffusionXL

# input_image_path = "./base.jpg"
# output_image_path = "generated_image.png"
# prompt = "Make her stand up, big tits, same lighting and high-end camera quality, rim lighting, looking at the camera, ultra quality, sharp focus, tack sharp, dof, film grain, 8K UHD, high detailed skin, high detailed skin, skin pores, like real insta-worthy"
# negative_prompt = "disfigured, ugly, bad, immature, cartoon, anime, 3d, painting, b&w, extra head, extra legs, extra arms, extra body"

# # 1. image generator
# sd_xl = StableDiffusionXL()
# sd_xl.generate_image(prompt, negative_prompt,
#                      num_inference_steps=30, high_noise_frac=0.8)


# IPAdapterFace 클래스 초기화
ip_adapter = IPAdapterFace()

# 이미지 생성
prompt = "Apply the face to the base image with a smiling expression"
base_image_path = "./base.jpg"
face_image_path = "./face.png"
output_image_path = "output_image.png"

ip_adapter.generate_image(base_image_path, face_image_path, prompt,
                          num_inference_steps=30, output_image_path=output_image_path)
