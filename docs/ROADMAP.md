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

### Milestone 2: Core Mesh Protocols (v3.0.x - High Priority)
- [ ] **v3.0.1 — Agent Registry**: Decentralized discovery mechanism via Nostr. Agents publish an `AgentCapability` event to allow discovery of specialized skills (TTS, Translation, etc.).
- [ ] **v3.0.2 — Standardized AgentMessage**: Unified communication protocol with common schema (id, sender, receiver, type, payload, timestamp).
- [ ] **v3.0.3 — Task Agent**: High-level orchestrator that receives requests and delegates to specialized agents (Content, Storage, Network).

---

## v3.1 — Product vs Infrastructure Expansion

### Product Features (UX & Quality)
- **Multi-speaker**: Dialogue between host and guest.
- **NotebookLM style**: Deep "discussion" generation between two host voices.
- **Long-form Support**: Handling episodes >60 min with automatic part splitting.

### Infrastructure Features (Performance & Scaling)
- **TTS Caching**: Content-addressed audio storage to avoid redundant synthesis.
- **Integrated Scheduling**: Internal agenda (APScheduler) for automated tasks.
- **Batch Processing**: Parallel generation for multiple sources.

---

## v3.5 — Coordination & Knowledge Mesh 💸

### Milestone 1: Workflow & Knowledge
- **Workflow Agent**: Manages complex task sequences (fetch → summarize → translate → script → audio → publish). Each step is assigned to the best available agent.
- **Knowledge Agent**: Evolution of the Social Agent. Manages distributed memory, shared knowledge graphs, and reputation via Nostr events.

### Milestone 2: Agentic Economy
- **agentstr-sdk Integration**: Professional A2A coordination and MCP compatibility.
- **Micropayments Layer**: Lightning Network and Cashu integration for pay-per-task execution.

---

## v4.0 — Decentralized Native Platform 🏛️

Evolution from a "Podcast Tool" to a generic distributed agentic infrastructure.

### Milestone 1: Project Agent (Strategic High-Value)
- **Project Agent**: Represents an autonomous project. Maintains state, coordinates members (human/agent), and manages memory on IPFS.

### Milestone 2: Decentralized Native Components
- **Identity Agent**: Sovereign identity management based on Nostr keys.
- **Reputation Agent**: feedback and trust scores for agents in the mesh.
- **Marketplace Agent**: Automated matching and bidding for agent services.
- **Federated Search Agent**: Distributed discovery across Nostr, IPFS, and local caches.

---

## Implementation Plan: v3.0.x (Immediate Focus)

1. **Registry**: Implement `AgentCapability` events (Nostr Kind 30311) for discovery.
2. **Protocol**: Finalize `AgentMessage` Pydantic model for signed P2P communication.
3. **Orchestration**: Deploy `TaskAgent` as the primary entry point for complex generation requests.

---

## Contributing

We welcome contributions to any part of the roadmap. Please open an issue to discuss your implementation plan before starting work.
Every new feature should follow the async-first pattern and include comprehensive tests.
