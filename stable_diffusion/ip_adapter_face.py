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

app = face_analysis.FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

images = ["./ip_adapter_face_id/face/1.jpg", "./ip_adapter_face_id/face/2.jpg", "./ip_adapter_face_id/face/3.jpg", "./ip_adapter_face_id/face/4.jpg", "./ip_adapter_face_id/face/5.jpg"]

faceid_embeds = []
for image in images:
    image = cv2.imread('base.jpg')
    faces = app.get(image)
    faceid_embeds.append(torch.from_numpy(faces[0].normed_embedding).unsqueeze(0).unsqueeze(0))
faceid_embeds = torch.cat(faceid_embeds, dim=1)

base_model_path = "SG161222/Realistic_Vision_V4.0_noVAE"
vae_model_path = "stabilityai/sd-vae-ft-mse"
ip_ckpt = "ip-adapter-faceid-portrait_sd15.bin"
device = "cuda"

noise_scheduler = DDIMScheduler(
    num_train_timesteps=1000,
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear",
    clip_sample=False,
    set_alpha_to_one=False,
    steps_offset=1,
)
vae = AutoencoderKL.from_pretrained(vae_model_path).to(dtype=torch.float16)
pipe = StableDiffusionPipeline.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    scheduler=noise_scheduler,
    vae=vae,
    feature_extractor=None,
    safety_checker=None
)


# load ip-adapter
ip_model = ip_adapter_faceid_separate.IPAdapterFaceID(pipe, ip_ckpt, device, num_tokens=16, n_cond=5)

# generate image
prompt = "photo of a woman in red dress in a garden"
negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality, blurry"

images = ip_model.generate(
    prompt=prompt, negative_prompt=negative_prompt, faceid_embeds=faceid_embeds, num_samples=4, width=512, height=512, num_inference_steps=30, seed=2023
)