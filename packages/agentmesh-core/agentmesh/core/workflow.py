import asyncio
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from agentmesh.core import BaseAgent, MeshConfig
from agentmesh.core.models import AgentMessage, AgentCapability

class WorkflowStep(BaseModel):
    name: str
    capability_required: str
    params: Dict[str, Any] = {}

class WorkflowAgent(BaseAgent):
    """
    Manages complex task sequences. It resolves which agents are needed
    using the Registry and coordinates execution via the Message Bus.
    """

    def __init__(self, config: MeshConfig, registry_agent=None):
        super().__init__(config)
        self.capabilities = ["workflow-orchestration", "sequence-management"]
        self.registry_agent = registry_agent # The agent that can search capabilities

    async def start(self):
        self.logger.info("WorkflowAgent ready.")

    async def stop(self):
        pass

    async def execute_workflow(self, steps: List[WorkflowStep]):
        """Executes a sequence of steps by finding and hiring appropriate agents."""
        self.logger.info(f"Executing workflow with {len(steps)} steps.")

        results = {}
        for step in steps:
            self.logger.info(f"Processing step: {step.name} (requires: {step.capability_required})")

            # 1. Find agents with the required capability
            if not self.registry_agent:
                self.logger.error("No registry agent available to resolve capabilities.")
                break

            providers = await self.registry_agent.search_capabilities(step.capability_required)
            if not providers:
                self.logger.error(f"No providers found for capability: {step.capability_required}")
                break

            # 2. Pick the first one (for now)
            provider = providers[0]
            self.logger.info(f"Hiring agent {provider.name} ({provider.public_key}) for {step.name}")

            # 3. Send Task Message
            msg = AgentMessage(
                sender=self.config.agent_id, # Should be the real pubkey in a full implementation
                receiver=provider.public_key,
                type="task",
                payload={
                    "action": step.name,
                    "params": step.params,
                    "context": results # Pass results of previous steps
                }
            )

            # In a real async mesh, we would wait for a response message.
            # For this PoC, we assume synchronous execution or local emulation.
            # await self.registry_agent.send_message(msg)

            # Placeholder for result collection
            results[step.name] = "completed"

        return results

    async def handle_message(self, message: AgentMessage):
        if message.message_type == "task" and message.payload.get("action") == "run_workflow":
            steps_data = message.payload.get("steps", [])
            steps = [WorkflowStep(**s) for s in steps_data]
            await self.execute_workflow(steps)
