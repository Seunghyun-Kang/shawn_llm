import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import warnings

class NanoLLaVAImageCaptioner:
    def __init__(self, model_name='qnguyen3/nanoLLaVA-1.5', device='cuda'):
        self.device = device
        torch.set_default_device(self.device)
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map='auto',
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        transformers.logging.set_verbosity_error()
        transformers.logging.disable_progress_bar()
        warnings.filterwarnings('ignore')

    def generate_caption(self, image_path, prompt='Make instagram caption which is related this image in detail'):
        messages = [
            {"role": "user", "content": f'<image>\n{prompt}'}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        text_chunks = [self.tokenizer(chunk).input_ids for chunk in text.split('<image>')]
        input_ids = torch.tensor(text_chunks[0] + [-200] + text_chunks[1], dtype=torch.long).unsqueeze(0)
        
        image = Image.open(image_path)
        image_tensor = self.model.process_images([image], self.model.config).to(dtype=self.model.dtype)
        
        output_ids = self.model.generate(
            input_ids,
            images=image_tensor,
            max_new_tokens=2048,
            use_cache=True
        )[0]
        
        return self.tokenizer.decode(output_ids[input_ids.shape[1]:], skip_special_tokens=True).strip()

if __name__ == "__main__":
    image_captioner = NanoLLaVAImageCaptioner()
    image_path = 'bot.png'
    caption = image_captioner.generate_caption(image_path)
    print(caption)
