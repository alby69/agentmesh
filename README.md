# AgentMesh

> **A decentralized coordination mesh for autonomous AI agents.**

AgentMesh is an open-source framework and ecosystem designed to build, deploy, and orchestrate AI agents in a truly decentralized environment. By combining **Nostr** for coordination, **IPFS** for storage, and a **Multi-Agent** architecture, AgentMesh enables a "serverless" future for AI applications.

---

## 🌟 The Vision

AgentMesh is not just software; it is an infrastructure for digital sovereignty.

- **No Central Servers**: No single point of failure. The system lives on users' nodes.
- **Sovereign Identity**: Every agent and user owns their cryptographic keys (Nostr).
- **Distributed Memory**: Data is stored on IPFS, making it permanent and content-addressable.
- **Agent-to-Agent (A2A) Collaboration**: Agents cooperate via open protocols, not proprietary APIs.

---

## 🏗️ Project Structure

The repository is organized as a monorepo managed with `uv`.

### Core Packages (`packages/`)
- **[`agentmesh-core`](packages/agentmesh-core)**: Foundational interfaces, models, and structured logging.
- **[`agentmesh-llm`](packages/agentmesh-llm)**: Unified provider interface for LLMs (Gemini, OpenAI, Anthropic, Ollama).
- **[`agentmesh-relay`](packages/agentmesh-relay)**: P2P communication layer based on the **Nostr** protocol.
- **[`agentmesh-vault`](packages/agentmesh-vault)**: Distributed storage layer based on **IPFS**.
- **[`agentmesh-studio`](packages/agentmesh-studio)**: CLI tools for mesh monitoring and management.

### Applications (`apps/`)
- **[`podcast-generator`](apps/podcast-generator)**: Complete pipeline transforming newsletters into podcasts.

---

## 🚀 Key Features

- **Decentralized CI/CD**: Automatic linting and testing via GitHub Actions.
- **Structured Logging**: Unified JSON logging for better observability in distributed nodes.
- **Security First**: Documented threat model and security best practices.
- **Standardized A2A**: Formal protocol for inter-agent tasking and responses.

---

## 🎙️ Use Case: Podcast Generator

```bash
# Install dependencies
uv sync
playwright install firefox

# Start generation via CLI
python apps/podcast-generator/main.py daily
```

---

## 📖 Documentation

| Document | Content |
|---|---|
| [docs/VISION.md](docs/VISION.md) | Philosophy and digital sovereignty |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Mesh layers and technical details |
| [docs/A2A_PROTOCOL.md](docs/A2A_PROTOCOL.md) | Communication standards |
| [docs/SECURITY.md](docs/SECURITY.md) | Threat model and mitigations |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Future plans and v4.0 focus |

---

## Contributing

We are in an intense development phase. See [docs/README.md](docs/README.md) for the full index of technical documentation.

**AgentMesh: The mesh is the message.**
