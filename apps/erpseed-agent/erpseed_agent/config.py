"""Pydantic Settings for erpseed-agent."""

from __future__ import annotations

from typing import List
from pydantic import Field
from pydantic_settings import SettingsConfigDict
from agentmesh.core.base import MeshConfig


class ERPSeedConfig(MeshConfig):
    model_config = SettingsConfigDict(
        env_prefix="ERPSEED_AGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    agent_id: str = Field(default="erpseed-builder-agent")
    agent_name: str = Field(default="ERPSeed Builder")
    agent_description: str = Field(
        default="Specialized agent for Enterprise Resource Planning operations, fiscal compliance, and dynamic model generation"
    )
    agent_version: str = Field(default="1.0.0")

    # Bridge configuration
    erpseed_base_url: str = Field(default="http://localhost:5000")
    erpseed_service_jwt: str = Field(default="")

    # Nostr / Relay configuration
    nostr_relay_url: str = Field(default="wss://relay.damus.io")
    nostr_relays: List[str] = Field(
        default_factory=lambda: ["wss://relay.damus.io", "wss://nos.lol", "wss://relay.snort.social"]
    )
    nostr_private_key: str = Field(default="")

    # IPFS / Vault configuration
    ipfs_gateway_url: str = Field(default="https://ipfs.io/ipfs/")
    ipfs_provider: str = Field(default="mock")
    ipfs_pinning_service: str = Field(default="")

    # LLM configuration
    llm_provider: str = Field(default="openai")
    llm_api_key: str = Field(default="")
    llm_model: str = Field(default="gpt-4o-mini")

    # Web server configuration
    web_host: str = Field(default="0.0.0.0")
    web_port: int = Field(default=8000)

    # Sync configuration
    sync_interval_seconds: int = Field(default=60)


def get_settings() -> ERPSeedConfig:
    return ERPSeedConfig()
