from typing import Optional, Any
from ..base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini"):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("openai is required for OpenAIProvider.")

        self.client = AsyncOpenAI(api_key=api_key)
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        model_name = model or self.default_model
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content.strip()
