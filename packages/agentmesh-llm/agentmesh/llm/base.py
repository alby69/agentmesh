from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """
        Generates text using the LLM provider.

        Args:
            prompt: The user prompt.
            system_instruction: Optional system instruction/prompt.
            model: Optional model name to override the default.
            **kwargs: Additional provider-specific arguments (e.g., tools).
        """
        pass
