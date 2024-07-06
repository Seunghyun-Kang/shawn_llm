import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline, ControlNetModel, StableDiffusionXLControlNetPipeline
from PIL import Image
from safetensors.torch import load_file, safe_open
from controlnet_aux import OpenposeDetector
from diffusers.utils import load_image

class StableDiffusionXL:
    def __init__(self, lora_paths=[], control_image=None):
        base_model_path = "./stable-diffusion-xl/sd_xl_base_1.0_0.9vae.safetensors"
        refiner_model_path = "./stable-diffusion-xl/sd_xl_refiner_1.0_0.9vae.safetensors"
        
        # 베이스 모델 로드
        if control_image:
            openpose = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
            image = Image.open(control_image)
            self.openpose_image = openpose(image)
            
            controlnet = ControlNetModel.from_pretrained("thibaud/controlnet-openpose-sdxl-1.0", torch_dtype=torch.float16)
        
            self.base_pipe = StableDiffusionXLControlNetPipeline.from_single_file(
            base_model_path, controlnet=controlnet, variant="fp16", torch_dtype=torch.float16).to("cuda")
        else:
            self.base_pipe = StableDiffusionXLPipeline.from_single_file(
            base_model_path, variant="fp16", torch_dtype=torch.float16).to("cuda")

        for lora_weights_path in lora_paths:
            self.apply_lora(self.base_pipe.unet, lora_weights_path)
        
        # 리파이너 모델 로드
        # self.refiner_pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
        #     refiner_model_path, variant="fp16", torch_dtype=torch.float16).to("cuda")

    def apply_lora(self, model, lora_weights_path):
        lora_weights = load_file(lora_weights_path)
        model.load_state_dict(lora_weights, strict=False)

    def generate_images(self, prompt, negative_prompt, num_images=1, num_inference_steps=30, high_noise_frac=0.8):
        
        images = []
        try:
            for _ in range(num_images):
                # 베이스 모델을 사용하여 이미지 생성 (잠재 공간에서)
                if self.openpose_image:
                    latent_image = self.base_pipe(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=num_inference_steps,
                        image = self.openpose_image.resize((1024, 1024)),
                        denoising_start=high_noise_frac,
                    ).images[0]
                else:
                    latent_image = self.base_pipe(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=num_inference_steps,
                        denoising_start=high_noise_frac,
                    ).images[0]

                # Refiner 모델을 사용하여 이미지 디테일 추가 (필요에 따라 주석 해제)
                # refined_image = self.refiner_pipe(
                #     prompt=prompt,
                #     negative_prompt=negative_prompt,
                #     num_inference_steps=num_inference_steps,
                #     denoising_start=high_noise_frac,
                #     image=latent_image
                # ).images[0]

                images.append(latent_image)

            return images
            
        except Exception as e:
            print(f"An error occurred: {e}")
