"""Pydantic Settings for erpseed-agent."""

from __future__ import annotations

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

    # Web server configuration
    web_host: str = Field(default="0.0.0.0")
    web_port: int = Field(default=8000)

    # Sync configuration
    sync_interval_seconds: int = Field(default=60)


def get_settings() -> ERPSeedConfig:
    return ERPSeedConfig()
