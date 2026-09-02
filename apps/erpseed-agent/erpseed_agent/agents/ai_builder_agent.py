"""AI Builder Agent wrapping ERPSeedBuilderService for low-code model, view, and workflow synthesis."""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.llm.builder_service import ERPSeedBuilderService
from erpseed_agent.bridge.executor import ERPSeedBridge

logger = logging.getLogger(__name__)


class AIBuilderAgent(ERPModuleAgent):
    """Specialized agent for low-code AI model, view, and workflow synthesis."""

    def __init__(
        self,
        config: ERPSeedConfig,
        builder_service: Optional[ERPSeedBuilderService] = None,
        bridge: Optional[ERPSeedBridge] = None,
    ):
        super().__init__(
            config=config,
            module_name="builder",
            capabilities=[
                "erp.builder.generate_model",
                "erp.builder.generate_view",
                "erp.builder.generate_workflow",
                "builder.generate_model",
                "builder.generate_view",
                "builder.generate_workflow",
            ],
            bridge=bridge,
        )
        self.builder_service = builder_service or ERPSeedBuilderService(config=config)

    async def generate_model(self, description: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        return await self.builder_service.generate_model(description=description, model_name=model_name)

    async def generate_view(self, model_name: str, view_type: str = "list") -> Dict[str, Any]:
        return await self.builder_service.generate_view(model_name=model_name, view_type=view_type)

    async def generate_workflow(self, workflow_name: str, description: str) -> Dict[str, Any]:
        return await self.builder_service.generate_workflow(workflow_name=workflow_name, description=description)
