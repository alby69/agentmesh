"""Pydantic Settings for podcast-generator."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── LLM ────────────────────────────────────────────────────────────
    llm_provider: str = Field(default="gemini")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.0-flash")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-3-5-haiku-latest")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3")

    # ── TTS ────────────────────────────────────────────────────────────
    tts_provider: str = Field(default="edge")
    tts_voice: str = Field(default="it-IT-GiuseppeNeural")
    host_voice: str = Field(default="it-IT-GiuseppeNeural")
    guest_voice: str = Field(default="it-IT-ElsaNeural")
    elevenlabs_api_key: str = Field(default="")
    elevenlabs_voice: str = Field(default="")
    elevenlabs_guest_voice: str = Field(default="")

    # ── Podcast ────────────────────────────────────────────────────────
    source_name: str = Field(default="newsletter")
    newsletter_url: str = Field(default="")
    archive_url: str = Field(default="")
    rss_urls: List[str] = Field(default_factory=list)
    language: str = Field(default="italiano")
    max_episode_minutes: int = Field(default=60)
    output_dir: Path = Field(default=Path("./output"))
    use_web_search: bool = Field(default=False)
    podcast_format: str = Field(default="monologue")
    intro_path: Optional[Path] = Field(default=None)
    outro_path: Optional[Path] = Field(default=None)

    # ── Web ────────────────────────────────────────────────────────────
    web_host: str = Field(default="0.0.0.0")
    web_port: int = Field(default=8000)
    web_password: str = Field(default="")
    api_token: str = Field(default="")
    ui_primary_color: str = Field(default="#2563eb")
    ui_accent_color: str = Field(default="#3b82f6")
    oauth_google_client_id: str = Field(default="")
    oauth_google_client_secret: str = Field(default="")
    oauth_github_client_id: str = Field(default="")
    oauth_github_client_secret: str = Field(default="")
    jwt_secret: str = Field(default="change-me")
    ipfs_provider: str = Field(default="mock")
    ipfs_gateway_url: str = Field(default="https://ipfs.io/ipfs/")

    # ── IMAP ───────────────────────────────────────────────────────────
    imap_host: str = Field(default="")
    imap_user: str = Field(default="")
    imap_password: str = Field(default="")
    imap_folder: str = Field(default="INBOX")
    imap_max_emails: int = Field(default=100)

    # ── Scraper ────────────────────────────────────────────────────────
    load_more_selector: str = Field(
        default="button:has-text('Load More'), a:has-text('Load More')"
    )
    link_pattern: str = Field(default="/p/")
    max_articles: int = Field(default=12)

    def model_post_init(self, __context):
        if not self.archive_url and self.newsletter_url:
            self.archive_url = f"{self.newsletter_url}/archive"

    def validate(self):
        from podcast_generator.exceptions import ConfigError

        missing = []
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        elif self.llm_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        elif self.llm_provider == "anthropic" and not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.archive_url:
            missing.append("NEWSLETTER_URL or ARCHIVE_URL")
        if missing:
            raise ConfigError(
                f"Missing required env vars: {', '.join(missing)}"
            )
