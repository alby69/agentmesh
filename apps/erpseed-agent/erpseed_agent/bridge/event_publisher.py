"""Event publisher bridge for relaying ERPSEED domain events to AgentMesh."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from agentmesh.core import AgentMessage

logger = logging.getLogger(__name__)


class EventPublisher:
    """Bridges internal ERPSEED domain events to Nostr / AgentMesh event stream."""

    def __init__(self, agent_id: str = "erpseed-builder-agent"):
        self.agent_id = agent_id

    async def publish_domain_event(
        self,
        event_name: str,
        payload: Dict[str, Any],
        target_pubkey: Optional[str] = None,
    ) -> AgentMessage:
        """
        Constructs an info/notification AgentMessage for an ERPSEED domain event.
        (e.g., 'order.confirmed', 'invoice.issued', 'stock.alert').
        """
        logger.info(f"Publishing ERPSEED domain event '{event_name}' to mesh (target: {target_pubkey or 'broadcast'})")
        return AgentMessage(
            sender=self.agent_id,
            receiver=target_pubkey,
            message_type="info",
            payload={
                "event": event_name,
                "data": payload,
            },
        )
