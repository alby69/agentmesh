import hashlib
from pathlib import Path
from typing import Optional
from agentmesh.core import BaseAgent, MeshConfig

class VaultAgent(BaseAgent):
    """Handles content-addressable storage using IPFS."""

    def __init__(self, config: MeshConfig, provider: str = "mock", gateway_url: str = "https://ipfs.io/ipfs/"):
        super().__init__(config)
        self.provider = provider
        self.gateway_url = gateway_url

    async def start(self):
        self.logger.info(f"VaultAgent started (Provider: {self.provider}).")

    async def stop(self):
        pass

    async def upload_file(self, filepath: Path) -> Optional[str]:
        """Uploads a file to IPFS and returns its CID."""
        if not filepath.exists():
            self.logger.error(f"File {filepath} does not exist.")
            return None

        if self.provider == "mock":
            file_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
            cid = f"Qm{file_hash[:44]}"
            self.logger.info(f"Mock upload successful. CID: {cid}")
            return cid

        # Real implementation for Pinata or Local Node would go here
        self.logger.warning(f"Provider {self.provider} not fully implemented in Core. Falling back to mock.")
        # Fix infinite recursion by using mock logic explicitly or returning None
        file_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
        return f"Qm{file_hash[:44]}"

    async def get_file_url(self, cid: str) -> str:
        return f"{self.gateway_url}{cid}"
