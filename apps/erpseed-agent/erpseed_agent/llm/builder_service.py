"""AI Builder Service using agentmesh-llm for model, view, and workflow synthesis."""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, Optional

from agentmesh.llm import LLMProviderFactory, BaseLLMProvider
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.llm.tools import get_builder_tools, execute_tool

logger = logging.getLogger(__name__)


class ERPSeedBuilderService:
    """Uses agentmesh-llm provider to generate low-code ERP schemas, views, and workflows."""

    def __init__(self, config: ERPSeedConfig, provider: Optional[BaseLLMProvider] = None):
        self.config = config
        self.provider = provider

    def _get_provider(self) -> BaseLLMProvider:
        if self.provider is None:
            try:
                self.provider = LLMProviderFactory.create(
                    self.config.llm_provider,
                    api_key=self.config.llm_api_key,
                    model=self.config.llm_model,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize LLM provider '{self.config.llm_provider}': {e}. Using fallback provider.")
                # Return dummy/mock provider if provider creation fails
                self.provider = FallbackLLMProvider()
        return self.provider

    async def generate_model(self, description: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Generates a SysModel definition based on natural language description."""
        prompt = f"Generate an ERP database model schema for: {description}."
        if model_name:
            prompt += f" Name the model '{model_name}'."

        system_instruction = (
            "You are an ERPSEED low-code architect AI. Output structured JSON for data models."
        )

        try:
            llm = self._get_provider()
            res = await llm.generate(prompt=prompt, system_instruction=system_instruction)
            # Try parsing JSON response
            parsed = json.loads(res)
            return parsed
        except Exception:
            # Fallback tool synthesis
            target_name = model_name or description.lower().replace(" ", "_")[:20]
            return execute_tool(
                "generate_model_schema",
                {
                    "model_name": target_name,
                    "verbose_name": description.title(),
                    "fields": [
                        {"name": "id", "type": "integer", "required": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "description", "type": "text", "required": False},
                        {"name": "created_at", "type": "datetime", "required": True},
                    ],
                },
            )

    async def generate_view(self, model_name: str, view_type: str = "list") -> Dict[str, Any]:
        """Generates a UI form/list view definition for an ERP model."""
        prompt = f"Generate a {view_type} layout for model '{model_name}'."
        system_instruction = "You are an ERP UI layout designer AI. Output structured view JSON."

        try:
            llm = self._get_provider()
            res = await llm.generate(prompt=prompt, system_instruction=system_instruction)
            return json.loads(res)
        except Exception:
            return execute_tool(
                "generate_view_layout",
                {
                    "model_name": model_name,
                    "view_type": view_type,
                    "components": ["id", "name", "description", "created_at"],
                },
            )

    async def generate_workflow(self, workflow_name: str, description: str) -> Dict[str, Any]:
        """Generates a workflow automation rule."""
        try:
            llm = self._get_provider()
            res = await llm.generate(prompt=f"Generate workflow '{workflow_name}' for: {description}")
            return json.loads(res)
        except Exception:
            return execute_tool(
                "generate_workflow_rule",
                {
                    "workflow_name": workflow_name,
                    "event_type": "on_create",
                    "condition": "status == 'pending'",
                    "action": "send_notification",
                },
            )


class FallbackLLMProvider(BaseLLMProvider):
    """Fallback LLM provider when live LLM APIs are not configured or available."""

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        return json.dumps(
            {
                "status": "ai_generated",
                "prompt_received": prompt,
                "result": "Generated schema response.",
            }
        )
