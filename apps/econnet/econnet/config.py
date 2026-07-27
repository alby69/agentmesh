from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    db_path: str = "apps/econnet/data/econnet.db"
    nostr_relay_urls: List[str] = ["wss://relay.damus.io", "wss://nos.lol"]
    nostr_private_key: str = ""
    nostr_publish: bool = False

    class Config:
        env_prefix = "ECONNET_"
        env_file = ".env"

settings = Settings()
