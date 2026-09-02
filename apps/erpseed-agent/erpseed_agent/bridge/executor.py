"""ERPSeed HTTP REST client bridge for executing CQRS commands and dynamic API operations."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class ERPSeedBridge:
    """HTTP bridge between AgentMesh and ERPSEED backend APIs."""

    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        service_jwt: str = "",
        timeout: float = 30.0,
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.service_jwt = service_jwt
        self.timeout = timeout
        self._client = client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _build_headers(self, tenant_id: int, api_key: str = "") -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": str(tenant_id),
        }
        token = api_key or self.service_jwt
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def health_check(self) -> bool:
        """Verifies connection and health status of ERPSEED backend."""
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return True
        except Exception:
            pass

        # Fallback check on capabilities endpoint
        try:
            response = await client.get(f"{self.base_url}/api/v1/ai/capabilities")
            return response.status_code < 500
        except Exception as e:
            logger.warning(f"ERPSeed backend health check failed at {self.base_url}: {e}")
            return False

    async def execute(
        self,
        action: str,
        params: Dict[str, Any],
        tenant_id: int = 1,
        api_key: str = "",
    ) -> Dict[str, Any]:
        """
        Executes an action against ERPSEED backend.

        Actions can be:
        - Domain command (e.g. 'sales.create_order', 'purchases.create_invoice')
        - Dynamic API CRUD (e.g. 'data.get', 'data.create', 'builder.generate_module')
        """
        client = await self._get_client()
        headers = self._build_headers(tenant_id=tenant_id, api_key=api_key)

        # Route action to corresponding ERPSEED endpoint
        if action.startswith("builder."):
            endpoint = f"{self.base_url}/api/v1/ai/builder"
            response = await client.post(endpoint, json={"action": action, **params}, headers=headers)
        elif action.startswith("data."):
            model = params.get("model", "entity")
            endpoint = f"{self.base_url}/api/v1/data/{model}"
            method = params.get("method", "POST").upper()
            if method == "GET":
                response = await client.get(endpoint, params=params.get("query", {}), headers=headers)
            else:
                response = await client.request(method, endpoint, json=params.get("data", params), headers=headers)
        else:
            # Generic CQRS action execution endpoint
            endpoint = f"{self.base_url}/api/v1/ai/execute"
            payload = {
                "command": action,
                "parameters": params,
            }
            response = await client.post(endpoint, json=payload, headers=headers)

        if response.status_code in (200, 201):
            try:
                return response.json()
            except Exception:
                return {"status": "success", "raw_response": response.text}

        logger.error(f"ERPSeed API error [{response.status_code}]: {response.text}")
        raise RuntimeError(
            f"ERPSeed API call for '{action}' failed with status {response.status_code}: {response.text}"
        )
