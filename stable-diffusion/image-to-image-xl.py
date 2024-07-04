import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
from PIL import Image
import numpy as np

input_image_path = "./C0GhdS0rEOg_0.jpg"
input_image = Image.open(input_image_path).convert("RGB")

# 단일 모델 로드
model_path = "./stable-diffusion-xl/sd_xl_base_1.0.safetensors"
refiner_model_path = "./stable-diffusion-xl/sd_xl_refiner_1.0.safetensors"

pipe = StableDiffusionXLPipeline.from_single_file(model_path, variant="fp16", torch_dtype=torch.float16)
# pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(model_path, variant="fp16", torch_dtype=torch.float16)
pipe = pipe.to("cuda")

refiner = StableDiffusionXLImg2ImgPipeline.from_single_file(refiner_model_path, variant="fp16", torch_dtype=torch.float16)
refiner = refiner.to("cuda")

prompt = "photo of beautiful Korean woman, big tits, same lighting and high-end camera quality,rim lighting, looking at the camera, ultra quality, sharp focus, tack sharp, dof, film grain, 8K UHD, high detailed skin, high detailed skin, skin pores, like real insta-worthy"
negative_prompt = "disfigured, ugly, bad, immature, cartoon, anime, 3d, painting, b&w, extra head, extra legs, extra arms, extra body"

try:
    # 이미지 생성
    num_inference_steps = 40
    high_noise_frac = 0.8

    # 베이스 모델을 사용하여 이미지 생성 (잠재 공간에서)
    latent_image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        # image=input_image,  # 추가된 부분: 입력 이미지
        num_inference_steps=num_inference_steps,
        denoising_end=high_noise_frac,
        output_type="latent"
    ).images[0]

    # Refiner 모델을 사용하여 이미지 디테일 추가
    refined_image = refiner(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        denoising_start=high_noise_frac,
        image=latent_image
    ).images[0]
    # 이미지 저장
    image_path = "generated_image.png"
    refined_image.save(image_path)
    print(f"Image saved at {image_path}")

except Exception as e:
    print(f"An error occurred: {e}")
