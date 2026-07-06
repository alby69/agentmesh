# AgentMesh Vault

The distributed storage layer for AgentMesh, based on **IPFS**.

## Features

- **Content-Addressable Storage**: Every file is identified by its hash (CID).
- **Multiple Providers**: Supports Pinata, local nodes, and mock providers for testing.
- **Persistence**: Ensures agent data and artifacts (like podcast audio) are stored permanently.

## Usage

```python
from agentmesh.vault.agent import VaultAgent

vault = VaultAgent(provider="pinata", api_key="...")
cid = vault.upload_file("path/to/file.mp3")
print(f"File stored at CID: {cid}")
```

## Structure

- `agentmesh.vault.agent`: Main interface for uploading and retrieving files from IPFS.
