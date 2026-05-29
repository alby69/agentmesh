from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        pass

class BaseTTSProvider(ABC):
    @abstractmethod
    async def generate_audio(self, text: str, output_path: str) -> str:
        pass
