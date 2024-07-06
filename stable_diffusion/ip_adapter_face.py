import sys
import os
import torch
import cv2
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import StableDiffusionPipeline, DDIMScheduler, AutoencoderKL
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from stable_diffusion.ip_adapter_face_id.ip_adapter import ip_adapter_faceid_separate 
from stable_diffusion.ip_adapter_face_id.insightface.app import face_analysis

class FaceIDGenerator:
    def __init__(self, device="cuda"):
        self.device = device
        self.app = face_analysis.FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        base_model_path = "SG161222/Realistic_Vision_V4.0_noVAE"
        vae_model_path = "stabilityai/sd-vae-ft-mse"
        ip_ckpt = "./ip_adapter_face_id/ip-adapter-faceid-plusv2_sdxl.bin"
        
        self.noise_scheduler = DDIMScheduler(
            num_train_timesteps=1000,
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            clip_sample=False,
            set_alpha_to_one=False,
            steps_offset=1,
        )
        
        self.vae = AutoencoderKL.from_pretrained(vae_model_path).to(dtype=torch.float16)
        self.pipe = StableDiffusionPipeline.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16,
            scheduler=self.noise_scheduler,
            vae=self.vae,
            feature_extractor=None,
            safety_checker=None
        )
        
        self.ip_model = ip_adapter_faceid_separate.IPAdapterFaceID(self.pipe, ip_ckpt, self.device, num_tokens=16, n_cond=5)

    def get_face_embeddings(self, face_model):
        default_face_id_paths = "./ip_adapter_face_id/face_id_sample/"
        folder_path = os.path.join(default_face_id_paths, face_model)
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"지정된 폴더 경로가 존재하지 않습니다: {folder_path}")

        image_extensions = ['.jpg', '.jpeg', '.png']
        image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]
        if len(image_paths) == 0:
            raise FileNotFoundError(f"지정된 폴더에 얼굴 데이터가 없습니다: {folder_path}")

        faceid_embeds = []
        for image_path in image_paths:
            image = cv2.imread(image_path)
            faces = self.app.get(image)
            if faces:
                faceid_embeds.append(torch.from_numpy(faces[0].normed_embedding).unsqueeze(0).unsqueeze(0))
        return torch.cat(faceid_embeds, dim=1)

    def generate_images(self, prompt, negative_prompt, faceid_embeds, num_samples=4, width=512, height=512, num_inference_steps=30, seed=2023):
        return self.ip_model.generate(
            prompt=prompt, 
            negative_prompt=negative_prompt, 
            faceid_embeds=faceid_embeds, 
            num_samples=num_samples, 
            width=width, 
            height=height, 
            num_inference_steps=num_inference_steps, 
            seed=seed
        )
