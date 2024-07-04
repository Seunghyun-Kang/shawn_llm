import torch
from diffusers import (
    StableDiffusionInstructPix2PixPipeline,
    AutoencoderKL,
    CLIPTextModel,
    CLIPTokenizer,
    UNet2DConditionModel,
    KarrasDiffusionSchedulers,
    StableDiffusionSafetyChecker,
    CLIPImageProcessor
)
from PIL import Image


class Pix2PixEditor:
    def __init__(self):
        torch.cuda.empty_cache()

        vae_path = "./instruct-pix2pix/vae"
        text_encoder_path = "./instruct-pix2pix/text_encoder"
        tokenizer_path = "./instruct-pix2pix/tokenizer"
        unet_path = "./instruct-pix2pix/unet"
        scheduler_path = "./instruct-pix2pix/scheduler"
        feature_extractor_path = "./instruct-pix2pix/feature_extractor"

        vae = AutoencoderKL.from_single_file(vae_path)
        text_encoder = CLIPTextModel.from_single_file(text_encoder_path)
        tokenizer = CLIPTokenizer.from_single_file(tokenizer_path)
        unet = UNet2DConditionModel.from_single_file(unet_path)
        scheduler = KarrasDiffusionSchedulers.from_single_file(scheduler_path)
        feature_extractor = CLIPImageProcessor.from_single_file(
            feature_extractor_path)

        self.pipe = StableDiffusionInstructPix2PixPipeline(
            vae=vae,
            text_encoder=text_encoder,
            tokenizer=tokenizer,
            unet=unet,
            scheduler=scheduler,
            safety_checker=None,
            feature_extractor=feature_extractor
        )

        self.pipe = self.pipe.to("cuda")

    def edit_image(self, input_image_path, prompt, negative_prompt="", num_inference_steps=30, output_image_path="edited_image.png"):
        input_image = Image.open(input_image_path).convert("RGB")

        try:
            # 이미지를 편집하여 생성
            edited_image = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=input_image,  # 입력 이미지
                num_inference_steps=num_inference_steps,
            ).images[0]

            # 이미지 저장
            edited_image.save(output_image_path)
            print(f"Image saved at {output_image_path}")

        except Exception as e:
            print(f"An error occurred: {e}")
