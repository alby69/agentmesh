# Roadmap

## v2.0 — Complete Restructuring (Completed)

### Objective
Transform the project into an **installable Python library** with a clean API, multi-LLM support, FastAPI web app, and documentation.
- **Runtime status**: Stable local runtime with async-first architecture.

---

## v3.0 — The Decentralized Era (Current Phase) 🚀

Transitioning from a monolithic architecture to a **P2P Multi-Agent** mesh.

### Milestone 1: Core Agent Framework (Completed)
- [x] **BaseAgent Framework**: Foundational infrastructure for decoupled asynchronous agents.
- [x] **Relay Agent (Nostr)**: Identity (NIP-01) and event propagation.
- [x] **Vault Agent (IPFS)**: Content-addressable storage using CIDs.
- [x] **Content Agent**: Core generation logic refactored as an agent.

### Milestone 2: Service Coordination & Protocol (In Progress)
- [ ] **v3.0.1 — Agent Registry (High Priority)**: Decentralized discovery mechanism. Agents publish capabilities as Nostr events so others can find "who can do TTS/Translation/etc."
- [ ] **v3.0.2 — Standardized AgentMessage**: Unified communication protocol for inter-agent tasks and payloads.
- [ ] **v3.0.3 — Task Agent**: The orchestrator that receives high-level requests and delegates them to specialized agents (Content, Storage, Network).
- [ ] **NIP-94 Integration**: Standardized file metadata events for better client compatibility.

---

## v3.1 — Enhancement & Scaling

### Product Features
- **Multi-speaker**: Dialogue between 2 voices (host + guest).
- **NotebookLM Style**: Deep discussion generation.
- **Long-form Podcasts**: Handling episodes >60 min.

### Infrastructure Features
- **TTS Caching**: Avoid regenerating audio for identical scripts.
- **Scheduling**: Built-in task scheduling.
- **Batch Processing**: Parallel generation workflows.

---

## v3.5 — Advanced Coordination & Workflow 💸

Focusing on the "Market of Cooperative Intelligences".

### Milestone 1: Workflow & Knowledge
- **Workflow Agent**: Manages complex sequences of tasks (fetch → summarize → translate → script → audio → publish).
- **Knowledge Agent**: Evolution of the Social Agent. Manages distributed memory, shared knowledge graphs, and reputation via Nostr.

### Milestone 2: agentstr-sdk & MCP
- **MCP Compatibility**: Exposing agent capabilities as Model Context Protocol tools.
- **Advanced A2A**: Integration of `agentstr-sdk` for professional-grade agent communication.
- **Micropayments (Lightning/Cashu)**: Pay-per-task execution (Routstr-style).

---

## v4.0 — Decentralized Native & Organizational Layer 🏛️

Shifting the focus from a "Podcast Tool" to a "Distributed Agentic Platform".

### Milestone 1: Project Agent (Strategic Value)
- **Project Agent**: An agent representing an autonomous project. Maintains state, coordinates members, and manages memory/communication for a specific goal.

### Milestone 2: Decentralized Infrastructure
- **Identity Agent**: Sovereign identity based solely on Nostr pubkeys.
- **Reputation Agent**: Trust scores based on verified feedback and work history in the mesh.
- **Marketplace Agent**: Automated matching between service providers and requestors.
- **Federated Search**: Distributed content discovery across Nostr, IPFS, and local caches.

---

## Implementation Plan (Current: v3.0.x)

We are currently focused on stabilizing the core mesh protocols:

1.  **Registry Implementation**: Defining the `AgentCapability` schema and Nostr event kind for discovery.
2.  **Message Protocol**: Finalizing the `AgentMessage` structure to ensure long-term compatibility.
3.  **Task Orchestration**: Introducing the `TaskAgent` to move away from direct user-to-content-agent interaction.

---

## Contributing

If you want to contribute:
1. Choose a feature from the roadmap.
2. Open an issue to discuss it.
3. Implement it with tests.
Every new feature should have tests (pytest) and follow the async-first pattern.
