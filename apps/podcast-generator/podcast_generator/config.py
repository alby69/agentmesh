from pathlib import Path
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from agentmesh.core import MeshConfig

class LLMConfig(BaseSettings):
    llm_provider: str = Field(default="gemini")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.0-flash")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-3-5-haiku-latest")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class TTSConfig(BaseSettings):
    tts_provider: str = Field(default="edge")
    tts_voice: str = Field(default="it-IT-GiuseppeNeural")
    host_voice: str = Field(default="it-IT-GiuseppeNeural")
    guest_voice: str = Field(default="it-IT-ElsaNeural")
    elevenlabs_api_key: str = Field(default="")
    elevenlabs_voice: str = Field(default="")
    elevenlabs_guest_voice: str = Field(default="")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class PodcastConfig(BaseSettings):
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class WebConfig(BaseSettings):
    web_port: int = Field(default=8000)
    web_host: str = Field(default="0.0.0.0")
    web_password: str = Field(default="")
    api_token: str = Field(default="")
    ui_primary_color: str = Field(default="#2563eb")
    ui_accent_color: str = Field(default="#3b82f6")
    oauth_google_client_id: str = Field(default="")
    oauth_google_client_secret: str = Field(default="")
    oauth_github_client_id: str = Field(default="")
    oauth_github_client_secret: str = Field(default="")
    jwt_secret: str = Field(default="change-me")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class IMAPConfig(BaseSettings):
    imap_host: str = Field(default="")
    imap_user: str = Field(default="")
    imap_password: str = Field(default="")
    imap_folder: str = Field(default="INBOX")
    imap_max_emails: int = Field(default=100)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class ScraperConfig(BaseSettings):
    load_more_selector: str = Field(default="button:has-text('Load More'), a:has-text('Load More')")
    link_pattern: str = Field(default="/p/")
    max_articles: int = Field(default=12)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Unified Settings for backward compatibility if needed,
# but components should preferably take specific configs.
class Settings(MeshConfig, LLMConfig, TTSConfig, PodcastConfig, WebConfig, IMAPConfig, ScraperConfig):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    def model_post_init(self, __context):
        if not self.archive_url and self.newsletter_url:
            self.archive_url = f"{self.newsletter_url}/archive"

    def validate(self):
        missing = []
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        elif self.llm_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        elif self.llm_provider == "anthropic" and not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.archive_url:
            missing.append("NEWSLETTER_URL o ARCHIVE_URL")
        if missing:
            from podcast_generator.exceptions import ConfigError
            raise ConfigError(f"Missing required env vars: {', '.join(missing)}")
