from typing import Dict, Type, Any
from .base import BaseLLMProvider
from .providers.gemini import GeminiProvider
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.ollama import OllamaProvider

class LLMProviderFactory:
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    @classmethod
    def create(cls, provider_name: str, **kwargs: Any) -> BaseLLMProvider:
        provider_cls = cls._providers.get(provider_name.lower())
        if not provider_cls:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
        return provider_cls(**kwargs)
