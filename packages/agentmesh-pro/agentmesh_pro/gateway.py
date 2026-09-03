"""Multi-Model Gateway for AgentMesh Pro using LiteLLM with multi-provider fallbacks."""

import logging
from typing import Any, Dict, List, Optional
from agentmesh_pro.config import settings

logger = logging.getLogger(__name__)


class ModelGateway:
    """LiteLLM-backed model gateway with automatic provider fallback."""

    def __init__(self, default_model: Optional[str] = None, fallback_model: Optional[str] = None):
        self.default_model = default_model or settings.default_model
        self.fallback_model = fallback_model or settings.fallback_model

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """Attempts generation using LiteLLM with primary model, then fallback model."""
        try:
            import litellm
            response = await litellm.acompletion(
                model=self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return {
                "content": content,
                "model_used": self.default_model,
                "status": "success",
            }
        except Exception as primary_error:
            logger.warning(f"Primary model ({self.default_model}) failed: {primary_error}. Retrying with fallback ({self.fallback_model}).")
            try:
                import litellm
                response = await litellm.acompletion(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content
                return {
                    "content": content,
                    "model_used": self.fallback_model,
                    "status": "fallback_success",
                }
            except Exception as fallback_error:
                logger.error(f"Fallback model ({self.fallback_model}) also failed: {fallback_error}.")
                # Simulated offline/mock response if API keys are missing or network is unavailable
                prompt_summary = messages[-1]["content"] if messages else "query"
                return {
                    "content": f"[Simulated Resilient Response] Processed query: '{prompt_summary}' via AgentMesh Pro Mesh Gateway.",
                    "model_used": "offline-fallback-simulator",
                    "status": "simulated_success",
                }


gateway = ModelGateway()
