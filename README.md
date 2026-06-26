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
- **[`agentmesh-core`](packages/agentmesh-core)**: The "brain" of the system. Defines base interfaces, orchestration, and LLM/TTS providers.
- **[`agentmesh-relay`](packages/agentmesh-relay)**: The P2P communication layer based on the **Nostr** protocol.
- **[`agentmesh-vault`](packages/agentmesh-vault)**: The distributed storage layer based on **IPFS**.
- **[`agentmesh-studio`](packages/agentmesh-studio)**: CLI tools and dashboards for monitoring and managing the mesh.

### Applications (`apps/`)
- **[`podcast-generator`](apps/podcast-generator)**: Our primary use case. A complete pipeline that transforms newsletters into podcasts in an autonomous and distributed manner.

---

## 🎙️ Use Case: Podcast Generator

**PodcastGen** is a demonstration of what AgentMesh can do. It transforms text content into audio episodes, distributes them via IPFS, and announces them on the Nostr network.

### Quick Start (PodcastGen)

```bash
# Install dependencies
uv sync
playwright install firefox

# Configure the environment
cp .env.example .env
# Edit .env with your API keys (Gemini, OpenAI, etc.)

# Start generation via CLI
python apps/podcast-generator/main.py daily

# Start the Web Interface
PYTHONPATH=apps/podcast-generator uvicorn podcast_generator.web.app:app --reload
```

See the [PodcastGen documentation](apps/podcast-generator/README.md) for more details.

---

## 🚀 Towards v3.0

We are actively migrating PodcastGen towards the AgentMesh v3.0 (Agent-Centric) architecture.
Key roadmap points include:
- Native integration with **agentstr-sdk** for **MCP** (Model Context Protocol) compatibility.
- Standardized **Agent-to-Agent (A2A)** communication protocol.
- Fully decentralized Web UI that queries Nostr relays.

See [docs/ROADMAP.md](docs/ROADMAP.md) for technical details.

---

## 📖 Documentation

| Document | Audience | Content |
|---|---|---|
| [docs/VISION.md](docs/VISION.md) | Everyone | The philosophy and "why" behind AgentMesh |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Developers | Technical details on the mesh layers |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Everyone | Development status and future plans |
| [apps/podcast-generator/README.md](apps/podcast-generator/README.md) | Users | Complete guide to the podcast app |

---

## Contributing

We are in an intense development phase. If you want to contribute to building a decentralized AI future, open an Issue or a Pull Request.

**AgentMesh: The mesh is the message.**
