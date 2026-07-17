# Roadmap

## v2.0 — Complete Restructuring (Completed)

Transformed the project into an installable Python library with clean API, multi-LLM support, FastAPI web app, and documentation.
- **Runtime status**: Stable local runtime with async-first architecture.

---

## v3.0 — The Decentralized Era (Completed)

Transitioned from monolithic architecture to a P2P Multi-Agent mesh.

### Milestone 1: Core Agent Framework
- [x] **BaseAgent Framework**: Foundational infrastructure for decoupled asynchronous agents.
- [x] **Relay Agent (Nostr)**: Identity (NIP-01) and event propagation.
- [x] **Vault Agent (IPFS)**: Content-addressable storage using CIDs.
- [x] **Content Agent**: Core generation logic refactored as an agent.

### Milestone 2: Core Mesh Protocols
- [x] **v3.0.1 — Agent Registry**: Decentralized discovery via Nostr `AgentCapability` events.
- [x] **v3.0.2 — AgentMessage**: Unified inter-agent communication protocol.
- [x] **v3.0.3 — Task Agent**: High-level orchestrator delegating to specialized agents.

---

## v3.1 — Scaling & Advanced Coordination (Completed)

### Strategic Agents
- [x] **Workflow Agent**: Complex task sequence management.
- [x] **Project Agent**: Autonomous project lifecycle coordination.

### Product Features
- [x] **Multi-speaker**: Dialogue between host and guest.
- [x] **NotebookLM style**: Deep discussion generation.
- [ ] **Long-form Support**: Episodes >60 min with automatic splitting.

### Infrastructure
- [x] **TTS Caching**: Content-addressed audio storage.
- [x] **Reactive Message Bus**: Nostr event-driven task triggering.
- [x] **Integrated Scheduling**: APScheduler for automated tasks.

---

## v3.5 — Knowledge Mesh & Economy (Completed)

### Knowledge & Reputation
- [x] **Knowledge Agent**: Distributed memory and shared knowledge graphs.
- [x] **Reputation System**: Web-of-Trust based scores.

### Agentic Economy
- [x] **agentstr-sdk Integration**: A2A coordination and MCP compatibility.
- [x] **Micropayments Layer**: Lightning Network and Cashu integration.

---

## v3.6 — Monorepo Standardization (Completed)

### Standardized App Template
- [x] **Scaffolding tool**: `scripts/new-app.sh` generates new apps from a standard template.
- [x] **Unified CLI**: All apps use `argparse` (stdlib) with `--server/--port/--host`.
- [x] **Unified Config**: Pydantic `BaseSettings` with `env_file=".env"`.
- [x] **Unified Web Stack**: FastAPI + Jinja2 + Tailwind + HTMX.
- [x] **Unified DB Layer**: Raw `sqlite3` with WAL mode, `data/` directory.
- [x] **Unified Tests**: pytest + conftest.py + TestClient + temp DB fixtures.

### App Refactoring
- [x] **newsletter-filter**: `__version__`, `.gitignore`, standardized DB path.
- [x] **podcast-generator**: Config flattened (7 mixins → 1), Typer → argparse, removed typer/rich deps.
- [x] **econnet**: `__version__`, `.gitignore`, `.env.example`, `conftest.py`.
- [x] **motedico**: Full scaffold from skeleton (main.py, config, web, db, tests, templates).

### Bug Fixes
- [x] **nostr-sdk API**: `Client(NostrSigner.keys(keys))` update, removed non-existent `Nip44`.
- [x] **podcast-generator tests**: Fixed mock paths, missing `ipfs_provider` config, env var timing.
- [x] **newsletter-filter DB**: Moved to `data/` directory, test DB in temp dir.

---

## v4.0 — Decentralized Native Platform

### Milestone 1: Advanced Identity & Discovery
- [ ] **Identity Agent**: Sovereign identity management (NIP-05, NIP-32), key rotation and recovery.
- [ ] **Federated Search Agent**: Distributed discovery across Nostr, IPFS, and local caches.
- [ ] **Capability Crawler**: Background agent indexing the mesh.

### Milestone 2: Agentic Marketplace
- [ ] **Marketplace Agent**: Automated matching and bidding for agent services.
- [ ] **Reputation Oracle**: Web-of-Trust signal aggregation.
- [ ] **Service Level Agreements (SLAs)**: Smart-contract-like task guarantees.

### Milestone 3: Infrastructure & UX
- [ ] **MCP Native Hub**: Full Model Context Protocol integration.
- [ ] **Mesh Dashboard**: Real-time P2P network visualization.
- [ ] **Mobile Node**: Lightweight agent runtime for mobile devices.

---

## Contributing

We welcome contributions. Please open an issue to discuss your plan before starting.
Every feature should follow the async-first pattern and include tests.
