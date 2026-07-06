from typing import Optional, Any
from ..base import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str, default_model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        model_name = model or self.default_model
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_instruction or ""},
                            {"role": "user", "content": prompt},
                        ],
                        "stream": False,
                        **kwargs
                    },
                    timeout=kwargs.get("timeout", 300),
                )
                response.raise_for_status()
                return response.json()["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}") from e
