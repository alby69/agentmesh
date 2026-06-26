# Roadmap

## v2.0 — Complete Restructuring (Completed)

### Objective
Transform the project into an **installable Python library** with a clean API, multi-LLM support, FastAPI web app, and documentation.
- **Runtime status**: Stable local runtime with async-first architecture.

---

## v3.0 — The Decentralized Era (Completed) 🚀

Transitioning from a monolithic architecture to a **P2P Multi-Agent** mesh.

### Milestone 1: Core Agent Framework
- [x] **BaseAgent Framework**: Foundational infrastructure for decoupled asynchronous agents.
- [x] **Relay Agent (Nostr)**: Identity (NIP-01) and event propagation.
- [x] **Vault Agent (IPFS)**: Content-addressable storage using CIDs.
- [x] **Content Agent**: Core generation logic refactored as an agent.

### Milestone 2: Core Mesh Protocols
- [x] **v3.0.1 — Agent Registry**: Decentralized discovery mechanism via Nostr. Agents publish an `AgentCapability` event to allow discovery of specialized skills (TTS, Translation, etc.).
- [x] **v3.0.2 — Standardized AgentMessage**: Unified communication protocol with common schema (id, sender, receiver, type, payload, timestamp).
- [x] **v3.0.3 — Task Agent**: High-level orchestrator that receives requests and delegates to specialized agents (Content, Storage, Network).

---

## v3.1 — Scaling & Advanced Coordination (Completed) 🚀

### Strategic Agents
- [x] **Workflow Agent**: Manages complex task sequences (fetch → summarize → translate → script → audio → publish). Resolves dependencies using the Registry.
- [x] **Project Agent**: Represents an autonomous project. Maintains state, coordinates members (human/agent), and manages project memory on IPFS.

### Product Features (UX & Quality)
- [x] **Multi-speaker**: Dialogue between host and guest.
- [x] **NotebookLM style**: Deep "discussion" generation between two host voices.
- [ ] **Long-form Support**: Handling episodes >60 min with automatic part splitting.

### Infrastructure Features (Performance & Scaling)
- [x] **TTS Caching**: Content-addressed audio storage to avoid redundant synthesis (Hash-based lookup).
- [x] **Reactive Message Bus**: Agents actively listen for Nostr events tagged with their pubkey to trigger tasks.
- [x] **Integrated Scheduling**: Internal agenda (APScheduler) for automated tasks.

---

## v3.5 — Knowledge Mesh & Economy (Completed) 💸

### Milestone 1: Knowledge & Reputation
- [x] **Knowledge Agent**: Evolution of the Social Agent. Manages distributed memory, shared knowledge graphs, and reputation via Nostr events.
- [x] **Reputation System**: Web-of-Trust based scores for mesh agents.

### Milestone 2: Agentic Economy
- [x] **agentstr-sdk Integration**: Professional A2A coordination and MCP compatibility.
- [x] **Micropayments Layer**: Lightning Network and Cashu integration for pay-per-task execution.

---

## v4.0 — Decentralized Native Platform 🏛️

Evolution from a "Podcast Tool" to a generic distributed agentic infrastructure.

- [ ] **Identity Agent**: Sovereign identity management based on Nostr keys.
- [ ] **Marketplace Agent**: Automated matching and bidding for agent services.
- [ ] **Federated Search Agent**: Distributed discovery across Nostr, IPFS, and local caches.

---

## Implementation Plan: v3.1 (Immediate Focus)

1. **Workflow**: Implement the `WorkflowAgent` to abstract multi-step sequences.
2. **Persistence**: Deploy `ProjectAgent` for long-running goal management.
3. **Efficiency**: Implement TTS Hashing and Caching via the Vault layer.

---

## Contributing

We welcome contributions to any part of the roadmap. Please open an issue to discuss your implementation plan before starting work.
Every new feature should follow the async-first pattern and include comprehensive tests.
