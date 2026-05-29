import aiohttp
import json
from pathlib import Path
from typing import Optional
from podcast_generator.agents.base import BaseAgent
from podcast_generator.config import Settings

class StorageAgent(BaseAgent):
    """Handles content-addressable storage using IPFS with support for different providers."""

    def __init__(self, config: Settings):
        super().__init__(config)
        self.provider = self.config.ipfs_provider
        self.gateway_url = self.config.ipfs_gateway_url
        self._cache = {} # Simple in-memory CID cache

    async def start(self):
        self.logger.info(f"StorageAgent started with provider: {self.provider}")

    async def stop(self):
        pass

    async def upload_file(self, filepath: Path) -> Optional[str]:
        """Uploads a file to IPFS and returns its CID."""
        if not filepath.exists():
            self.logger.error(f"File {filepath} does not exist.")
            return None

        # Check cache
        file_stats = filepath.stat()
        cache_key = f"{filepath}_{file_stats.st_mtime}_{file_stats.st_size}"
        if cache_key in self._cache:
            self.logger.info(f"Returning cached CID for {filepath}")
            return self._cache[cache_key]

        cid = None
        if self.provider == "pinata":
            cid = await self._upload_to_pinata(filepath)
        elif self.provider == "local":
            cid = await self._upload_to_local_node(filepath)
        else:
            cid = await self._mock_upload(filepath)

        if cid:
            self._cache[cache_key] = cid
        return cid

    async def _mock_upload(self, filepath: Path) -> str:
        self.logger.info(f"MOCK Uploading {filepath} to IPFS...")
        import hashlib
        file_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
        mock_cid = f"Qm{file_hash[:44]}"
        return mock_cid

    async def _upload_to_pinata(self, filepath: Path) -> Optional[str]:
        self.logger.info(f"Uploading {filepath} to Pinata...")
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": self.config.ipfs_api_key,
            "pinata_secret_api_key": self.config.ipfs_api_secret
        }

        try:
            async with aiohttp.ClientSession() as session:
                with open(filepath, 'rb') as f:
                    form = aiohttp.FormData()
                    form.add_field('file', f, filename=filepath.name)
                    async with session.post(url, data=form, headers=headers) as response:
                        if response.status == 200:
                            res_json = await response.json()
                            return res_json.get("IpfsHash")
                        else:
                            self.logger.error(f"Pinata upload failed: {response.status} {await response.text()}")
        except Exception as e:
            self.logger.error(f"Error uploading to Pinata: {e}")
        return None

    async def _upload_to_local_node(self, filepath: Path) -> Optional[str]:
        self.logger.info(f"Uploading {filepath} to local IPFS node...")
        url = "http://127.0.0.1:5001/api/v0/add"
        try:
            async with aiohttp.ClientSession() as session:
                with open(filepath, 'rb') as f:
                    form = aiohttp.FormData()
                    form.add_field('file', f, filename=filepath.name)
                    async with session.post(url, data=form) as response:
                        if response.status == 200:
                            res_json = await response.json()
                            return res_json.get("Hash")
                        else:
                            self.logger.error(f"Local IPFS upload failed: {response.status}")
        except Exception as e:
            self.logger.error(f"Error uploading to local IPFS: {e}")
        return None

    async def get_file_url(self, cid: str) -> str:
        """Returns a public gateway URL for a given CID."""
        return f"{self.gateway_url}{cid}"
