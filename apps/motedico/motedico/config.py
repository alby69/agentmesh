"""Pydantic Settings for motedico."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Web
    web_host: str = Field(default="0.0.0.0")
    web_port: int = Field(default=8000)

    # LLM
    llm_provider: str = Field(default="gemini")


def get_settings() -> Settings:
    return Settings()
