# Roadmap

## v2.0 — Complete Restructuring (Completed)

### Objective
Transform the project into an **installable Python library** with a clean API, multi-LLM support, FastAPI web app, and documentation.

### Achievements
- **Library Architecture**: `podcast_generator/` package.
- **Configuration**: Pydantic Settings V2.
- **Web App**: FastAPI, sqlite3, REST API, RSS feed.
- **Sources**: RSS & IMAP support.
- **Authentication**: OAuth (Google/GitHub) + JWT.

---

## v3.0 — The Decentralized Era (In Progress) 🚀

The transition from a monolithic architecture to a **P2P Multi-Agent** mesh.

### Milestone 1: Core Agent Framework (Completed)
- [x] **BaseAgent Framework**: Foundational infrastructure for decoupled asynchronous agents.
- [x] **Relay Agent (Nostr)**: Identity (NIP-01) and event propagation.
- [x] **Vault Agent (IPFS)**: Content-addressable storage using CIDs.
- [x] **Content Agent**: Core generation logic (Scraping, LLM, TTS) refactored as an agent.

### Milestone 2: Service Coordination (Current Focus)
- [ ] **Social Agent**: Monitoring Nostr relays for discovery and community interactions.
- [ ] **Discovery Protocol**: Implementing a Routstr-style registry for agent capabilities.
- [ ] **NIP-94 Integration**: Standardized file metadata events for better client compatibility.
- [ ] **LRU Cache for IPFS**: Efficient management of local content storage.

### Milestone 3: Decentralized Web Experience (v3.1)
- [ ] **Nostr-driven UI**: Refactoring the Web App to query relays instead of a local SQLite database.
- [ ] **Edge Playback**: Audio player that fetches content directly from IPFS gateways.
- [ ] **WebSocket Progress**: Real-time generation feedback via mesh events.
- [ ] **Mesh Studio CLI**: Enhanced dashboard for managing node identity and storage.

---

## v3.5 — Agentic Economy & A2A (Future) 💸

Transitioning into a "Market of Cooperative Intelligences".

### Milestone 1: `agentstr-sdk` & MCP Integration
- [ ] **MCP Compatibility**: Exposing agent capabilities as Model Context Protocol tools.
- [ ] **Advanced A2A**: Standardized communication for agents hiring other agents.

### Milestone 2: Micropayments Layer
- [ ] **Lightning/Cashu Integration**: Pay-per-task execution.
- [ ] **Automated Bidding**: Agents negotiate prices for sub-tasks (e.g., Content Agent hiring a Translation Agent).

---

## v4.0 — Production Grade & Multi-tenancy 🏛️

- [ ] **Full Multi-user Support**: Sovereign identity management for end-users.
- [ ] **PostgreSQL Support**: Enterprise-grade persistence for large-scale deployments.
- [ ] **Cloud-Mesh Hybrid**: Seamless failover between local IPFS and S3-based pinning services.
- [ ] **Unified CI/CD**: Automated testing and deployment for the entire monorepo.

---

## Contributing

If you want to contribute:
1. Choose a feature from the roadmap.
2. Open an issue to discuss it.
3. Implement it with tests.
4. Open a PR.

Every new feature should:
- Have tests (pytest).
- Be documented in `docs/`.
- Follow the project pattern (async first, Pydantic models).
