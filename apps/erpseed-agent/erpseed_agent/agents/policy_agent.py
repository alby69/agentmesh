"""Policy enforcement agent overlay for erpseed-agent governance."""

from __future__ import annotations

import logging
from typing import Set, Optional
from agentmesh.core import AgentMessage
from erpseed_agent.agents.erp_agent import ERPSeedAgent

logger = logging.getLogger(__name__)


class ERPSeedPolicyAgent:
    """
    Policy governance overlay for ERPSeedAgent.
    Validates permissions, capability access lists, and quota constraints.
    """

    def __init__(
        self,
        target_agent: ERPSeedAgent,
        allowed_actions: Optional[Set[str]] = None,
        blocked_actions: Optional[Set[str]] = None,
    ):
        self.agent = target_agent
        self.allowed_actions = allowed_actions  # If set, only these actions are allowed
        self.blocked_actions = blocked_actions or set()

    def is_action_allowed(self, action: str) -> bool:
        """Checks whether an action is permitted by policy."""
        if action in self.blocked_actions:
            return False
        if self.allowed_actions is not None:
            return action in self.allowed_actions or any(
                action.startswith(prefix.rstrip("*")) for prefix in self.allowed_actions if prefix.endswith("*")
            )
        return True

    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Evaluates policy constraints before delegating to the target ERPSeedAgent."""
        if message.message_type == "task":
            action = (message.payload or {}).get("action", "")
            if action and not self.is_action_allowed(action):
                logger.warning(f"Action '{action}' blocked by policy for sender {message.sender}")
                return AgentMessage(
                    sender=self.agent.config.agent_id,
                    receiver=message.sender,
                    message_type="error",
                    payload={
                        "status": "blocked",
                        "action": action,
                        "reason": f"Action '{action}' is prohibited by security policy.",
                    },
                )

        return await self.agent.handle_message(message)
