import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline, DDPMScheduler, UNet2DConditionModel, AutoencoderKL
from transformers import CLIPTextModel, CLIPTokenizer, CLIPImageProcessor
from PIL import Image

input_image_path = "./C0GhdS0rEOg_0.jpg"
input_image = Image.open(input_image_path).convert("RGB")

# 단일 모델 로드
model_path = "./stable-diffusion-xl/sd_xl_base_1.0.safetensors"
refiner_model_path = "./stable-diffusion-xl/sd_xl_refiner_1.0.safetensors"

pipe = StableDiffusionXLPipeline.from_single_file(model_path, torch_dtype=torch.float16)
pipe = pipe.to("cpu")

refiner = StableDiffusionXLImg2ImgPipeline.from_single_file(refiner_model_path, torch_dtype=torch.float16)
refiner = refiner.to("cpu")
# pipe = StableDiffusionImg2ImgPipeline(
#     vae=vae,
#     text_encoder=text_encoder,
#     tokenizer=tokenizer,
#     unet=unet,
#     scheduler=scheduler,
#     feature_extractor=feature_extractor,
#     safety_checker=None
# )


prompt = "photo of young Korean woman, black hair, sitting outside restaurant, wearing sexy bikini, rim lighting, instagram lighting, looking at the camera, iphone camera, ultra quality, sharp focus, tack sharp, dof, film grain, Fujifilm XT3, crystal clear, 8K UHD, high detailed skin, skin pores, like real instagram photo"
negative_prompt = "disfigured, ugly, bad, immature, cartoon, anime, 3d, painting, b&w, extra head, extra legs, extra arms"

try:
    image = pipe(
        prompt=prompt,
            negative_prompt=negative_prompt,
        num_inference_steps=30,
        denoising_start=0.8,
        output_type="latent",
    ).images

    image = refiner(
        prompt=prompt,
        image=image,
        num_inference_steps=30,
        denoising_start=0.8,
    ).images[0]

except Exception as e:
    print(f"An error occurred: {e}")