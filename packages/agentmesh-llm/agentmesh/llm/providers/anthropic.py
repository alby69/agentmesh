from typing import Optional, Any
from ..base import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, default_model: str = "claude-3-5-haiku-latest"):
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError("anthropic is required for AnthropicProvider.")

        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = default_model

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        model_name = model or self.default_model

        # Default max_tokens if not provided
        if "max_tokens" not in kwargs:
            kwargs["max_tokens"] = 8192

        response = await self.client.messages.create(
            model=model_name,
            system=system_instruction or "",
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.content[0].text.strip()
