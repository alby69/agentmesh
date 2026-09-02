"""Capability synchronization module for pulling tool manifests from ERPSEED and converting to AgentMesh capabilities."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import httpx
from agentmesh.core import AgentCapability
from erpseed_agent.web.db import update_capability_cache

logger = logging.getLogger(__name__)


class CapabilitySync:
    """Polls ERPSEED /api/v1/ai/capabilities and translates into AgentCapability definitions."""

    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        service_jwt: str = "",
        agent_id: str = "erpseed-builder-agent",
        public_key: str = "npub_erpseed_agent",
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.service_jwt = service_jwt
        self.agent_id = agent_id
        self.public_key = public_key
        self._client = client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def fetch_and_translate(self) -> List[AgentCapability]:
        """
        Fetches /api/v1/ai/capabilities manifest from ERPSEED
        and converts entries into AgentMesh AgentCapability objects.
        """
        client = await self._get_client()
        headers = {}
        if self.service_jwt:
            headers["Authorization"] = f"Bearer {self.service_jwt}"

        capabilities: List[AgentCapability] = []
        raw_capabilities: List[Dict[str, Any]] = []

        try:
            url = f"{self.base_url}/api/v1/ai/capabilities"
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                manifest = data.get("manifest", [])
                for agent_entry in manifest:
                    category = agent_entry.get("agent", "erp")
                    for cap in agent_entry.get("capabilities", []):
                        cap_name = cap.get("name", "")
                        cap_desc = cap.get("description", "")
                        input_schema = cap.get("input_schema", cap.get("parameters", {}))

                        agent_cap = AgentCapability(
                            agent_id=self.agent_id,
                            name=cap_name,
                            description=cap_desc,
                            version="1.0.0",
                            public_key=self.public_key,
                            capabilities=[cap_name],
                            metadata={
                                "category": category,
                                "input_schema": input_schema,
                            },
                        )
                        capabilities.append(agent_cap)
                        raw_capabilities.append(
                            {
                                "name": cap_name,
                                "description": cap_desc,
                                "category": category,
                                "input_schema": input_schema,
                            }
                        )

                # Persist in SQLite capability cache
                if raw_capabilities:
                    update_capability_cache(raw_capabilities)
                    logger.info(f"Synchronized {len(raw_capabilities)} capabilities from ERPSEED backend.")

        except Exception as e:
            logger.warning(f"Failed to fetch capabilities from ERPSEED at {self.base_url}: {e}")

        return capabilities
