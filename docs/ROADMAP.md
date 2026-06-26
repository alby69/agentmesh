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

### Milestone 1: Advanced Identity & Discovery
- [ ] **Identity Agent**: Sovereign identity management based on Nostr keys (NIP-05, NIP-32). Standardized key rotation and recovery.
- [ ] **Federated Search Agent**: Distributed discovery across Nostr, IPFS, and local caches using the "Routstr" pattern.
- [ ] **Capability Crawler**: Background agent that indexes the mesh and updates local knowledge graphs.

### Milestone 2: Agentic Marketplace
- [ ] **Marketplace Agent**: Automated matching and bidding (Service Announcements) for agent services using Nostr-native auctions.
- [ ] **Reputation Oracle**: Aggregates Web-of-Trust signals and task completion history to rank mesh participants.
- [ ] **Service Level Agreements (SLAs)**: Smart-contract-like templates for task guarantees via DLCs or multisig.

### Milestone 3: Infrastructure & UX
- [ ] **MCP Native Hub**: Full Model Context Protocol integration. Every agent becomes an MCP server and client.
- [ ] **Mesh Dashboard**: Real-time visualization of the P2P network, task flows, and agent economy.
- [ ] **Mobile Node**: Lightweight implementation for running agents on mobile devices (Android/iOS).

---

## Implementation Plan: v4.0 (Immediate Focus)

1. **Identity Refactor**: Integrate `agentstr-sdk` to handle sovereign identity and NIP-05 verification.
2. **Discovery Protocols**: Implement the "Routstr" discovery mechanism to replace simple relay-based lookup.
3. **A2A Bidding**: Deploy the first prototype of the Marketplace Agent with support for automated bidding.

---

## Contributing

We welcome contributions to any part of the roadmap. Please open an issue to discuss your implementation plan before starting work.
Every new feature should follow the async-first pattern and include comprehensive tests.
