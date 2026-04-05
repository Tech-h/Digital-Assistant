# === Standard Library ===
import httpx
from typing import Iterator, Any

# === Third-Party ===
from ollama import Client


class ResponseGenerator:
    def __init__(self, model: str, host: str, system_prompt: str, temp: float, num_ctx: int) -> None:
        self.client: Client = Client(
            host=host, timeout=httpx.Timeout(5.0, read=60.0)
        )
        
        self.model = model
        self.system_prompt = system_prompt
        self.options: dict[str, Any] = {
            'temperature': temp,
            'num_ctx': num_ctx
        }
    
    def generate_response(self, prompt: str) -> Iterator[str]: 
        full_prompt = (
            f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n"
            f"{prompt}" 
            f"<|im_start|>assistant\n"
        )
        
        response = self.client.generate(
            model=self.model,
            prompt=full_prompt,
            options={
                **self.options,
                'stop': ["<|im_start|>", "<|im_end|>", "im_start", "im_end"] 
            },
            stream=True
        )
        
        for chunk in response:
            content = chunk.get('response', '')
            if content:
                yield content