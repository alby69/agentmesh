import os
from typing import Optional
from ..interfaces import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise ImportError("google-genai is required for GeminiProvider. Install it with `pip install google-genai`.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        # Note: google-genai 1.0+ uses a different API structure, usually sync or has specific async methods
        # For simplicity in this extraction, we wrap the call.
        # In a real implementation we would use the proper async client if available.
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={"system_instruction": system_instruction} if system_instruction else None
        )
        return response.text

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("openai is required for OpenAIProvider.")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content
