"""Configuration settings for AgentMesh Pro."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentMesh Pro"
    version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # PostgreSQL & PGVector settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "agentmesh_pro"

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"

    # LLM Gateway settings
    default_model: str = "openai/gpt-4o-mini"
    fallback_model: str = "anthropic/claude-3-haiku-20240307"

    # Langfuse Observability settings
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
