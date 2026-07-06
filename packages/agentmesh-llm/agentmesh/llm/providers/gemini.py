from typing import Optional, Any
from ..base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, default_model: str = "gemini-2.0-flash"):
        try:
            from google import genai
        except ImportError:
            raise ImportError("google-genai is required for GeminiProvider.")

        self.client = genai.Client(api_key=api_key)
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        model_name = model or self.default_model
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction

        # Merge additional kwargs into config (e.g., tools)
        config.update(kwargs)

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        return response.text.strip()
