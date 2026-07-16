from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List

class FilterSettings(BaseSettings):
    # LLM settings
    llm_provider: str = Field(default="openai", env="FILTER_LLM_PROVIDER")
    llm_api_key: Optional[str] = Field(default=None, env="FILTER_LLM_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", env="FILTER_LLM_MODEL")

    # IMAP email retrieval settings
    imap_host: str = Field(default="", env="FILTER_IMAP_HOST")
    imap_user: str = Field(default="", env="FILTER_IMAP_USER")
    imap_password: str = Field(default="", env="FILTER_IMAP_PASSWORD")
    imap_folder: str = Field(default="INBOX", env="FILTER_IMAP_FOLDER")

    # RSS settings
    rss_urls: List[str] = Field(default_factory=list, env="FILTER_RSS_URLS")

    # Filtering default settings
    default_query: str = Field(
        default="Risorse Umane e Intelligenza Artificiale, impatto dell'AI sul lavoro e HR",
        env="FILTER_DEFAULT_QUERY"
    )

    # Inter-App Communication Pipeline settings
    podcast_gen_url: str = Field(
        default="http://localhost:8000",
        env="FILTER_PODCAST_GEN_URL"
    )
    podcast_gen_api_token: str = Field(
        default="",
        env="FILTER_PODCAST_GEN_API_TOKEN"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
