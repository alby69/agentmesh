# AgentMesh: The Coordination Mesh

AgentMesh is a decentralized multi-agent system architecture designed for the AI-native web.

## Components

### Core (`agentmesh-core`)
The brain of the system. It defines how agents interact, how they are orchestrated, and provides abstract interfaces for LLMs and TTS.

### Relay (`agentmesh-relay`)
The communication layer. Powered by **Nostr**, it handles identity and P2P event propagation.

### Vault (`agentmesh-vault`)
The storage layer. Powered by **IPFS**, it ensures content-addressable and permanent data storage.

## Vision: Coordination Mesh
Unlike traditional social networks, AgentMesh is a "mesh" of cooperative agents.
- **Identity**: Controlled by private keys (Nostr).
- **Communication**: P2P events.
- **Storage**: Distributed filesystem.
- **Intelligence**: Content agents that index, summarize, and curate the mesh.
