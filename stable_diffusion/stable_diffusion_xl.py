import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
from PIL import Image


class StableDiffusionXL:
    def __init__(self):
        # GPU 메모리 캐시 비우기
        torch.cuda.empty_cache()

        base_model_path = "./stable-diffusion-xl/sd_xl_base_1.0.safetensors"
        refiner_model_path = "./stable-diffusion-xl/sd_xl_refiner_1.0.safetensors"
        # 베이스 모델 로드
        self.base_pipe = StableDiffusionXLPipeline.from_single_file(
            base_model_path, variant="fp16", torch_dtype=torch.float16)
        self.base_pipe = self.base_pipe.to("cuda")

        # 리파이너 모델 로드
        self.refiner_pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
            refiner_model_path, variant="fp16", torch_dtype=torch.float16)
        self.refiner_pipe = self.refiner_pipe.to("cuda")

    def generate_image(self, prompt, negative_prompt, num_inference_steps=30, high_noise_frac=0.8, output_image_path="generated_image.png"):
        try:
            # 베이스 모델을 사용하여 이미지 생성 (잠재 공간에서)
            latent_image = self.base_pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                denoising_end=high_noise_frac,
                output_type="latent"
            ).images[0]

            # Refiner 모델을 사용하여 이미지 디테일 추가
            refined_image = self.refiner_pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                denoising_start=high_noise_frac,
                image=latent_image
            ).images[0]

            # 이미지 저장
            refined_image.save(output_image_path)
            print(f"Image saved at {output_image_path}")

        except Exception as e:
            print(f"An error occurred: {e}")
