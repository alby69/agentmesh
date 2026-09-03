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

## v3.7 — Enterprise Mesh & ERP Domain (Completed)

### erpseed-agent Integration
- [x] **Sovereign ERPSeedAgent**: Decentralized ERP integration subclassing `NostrAgent` with capability manifest sync.
- [x] **Domain Sub-agents**: Modular sub-agents for Sales, Purchases, Inventory, Accounting, HR, Manufacturing, CRM, Fattura Elettronica, Workflow, and AI Builder.
- [x] **Vault Bridge**: Content-addressed document storage on IPFS via `ERPSeedVaultBridge` (`agentmesh-vault`).
- [x] **FatturaPA 1.2 Compliance**: XML invoice synthesis and SDI gateway submit hooks.
- [x] **Dynamic Low-Code SysModel Engine**: NL-to-schema synthesis (`agentmesh-llm`) and dynamic CRUD endpoints (`data.<model>.<crud>`).
- [x] **Operator Web UI**: FastAPI + Jinja2 + HTMX operator dashboard supporting `/builder`, `/modules`, `/invoices`, `/workflows`, `/mesh`, `/vault`.

### agentmesh-pro Framework Extraction & Server Refactor
- [x] **Framework Extraction**: Extracted execution primitives (LangGraph orchestrator, LiteLLM gateway, PGVector/Redis persistence, Langfuse tracer, Pydantic schemas) into reusable `packages/agentmesh-pro`.
- [x] **Server Shell**: Created lightweight `apps/agentmesh-pro-server` FastAPI application consuming `agentmesh-pro`.

---

## v4.0 — Decentralized Native Platform

### Milestone 1: Advanced Identity & Discovery

Goal: Move from basic NIP-01 keypairs to a full sovereign identity layer with automated mesh discovery.

#### Epic: Identity Agent (`packages/agentmesh-identity`)
- **Description**: Sovereign identity management beyond raw Nostr keys.
- **Acceptance Criteria**:
  - [ ] `IdentityAgent` class extending `BaseAgent` with NIP-05 (DNS-based identifier) support.
  - [ ] NIP-32 (Labeling) integration for agent capability tagging.
  - [ ] Key rotation protocol: publish `KeyRotationEvent` (custom kind) and peer auto-update trust store.
  - [ ] Key recovery via Shamir's Secret Sharing (SSS): M-of-N shard reconstruction.
  - [ ] Identity revocation: publish revocation event to Nostr relays, cached by peers.
- **Dependencies**: `agentmesh-core`, `agentmesh-relay`, `nostr-sdk`
- **Estimated Complexity**: High
- **Target Version**: v4.0.0-alpha

#### Epic: Federated Search Agent
- **Description**: Distributed search across Nostr events, IPFS CIDs, and local agent caches without a central index.
- **Acceptance Criteria**:
  - [ ] `FederatedSearchAgent` that broadcasts `SearchQuery` events to the mesh.
  - [ ] Peers respond with `SearchResult` events containing relevance scores.
  - [ ] Result aggregation with deduplication (by CID/event-id).
  - [ ] Local cache indexing using `sqlite-fts5` for fast local lookup.
  - [ ] Fallback to Nostr relay search if mesh peers are offline.
- **Dependencies**: `agentmesh-core`, `agentmesh-relay`, `agentmesh-vault`
- **Estimated Complexity**: Medium
- **Target Version**: v4.0.0-beta

#### Epic: Capability Crawler
- **Description**: Background agent that continuously indexes the mesh for available services.
- **Acceptance Criteria**:
  - [ ] Subscribes to `AgentCapability` events (Kind 30311) on all configured relays.
  - [ ] Maintains a local SQLite cache of `agent_id -> capabilities -> last_seen`.
  - [ ] Expires stale entries after configurable TTL (default 24h).
  - [ ] Exposes `crawler.find_agents(capability="text-generation")` API.
  - [ ] Periodic re-broadcast of crawler's own capability index.
- **Dependencies**: `agentmesh-core`, `agentmesh-relay`
- **Estimated Complexity**: Low
- **Target Version**: v4.0.0-alpha

---

### Milestone 2: Agentic Marketplace

Goal: Enable agents to offer, discover, and pay for services autonomously.

#### Epic: Marketplace Agent (`packages/agentmesh-marketplace`)
- **Description**: Decentralized service marketplace where agents publish offers and bids.
- **Acceptance Criteria**:
  - [ ] `ServiceOffer` Pydantic model: `{service_type, price_msat, sla, agent_pubkey, expires_at}`.
  - [ ] `ServiceBid` model: `{task_description, max_price_msat, deadline, requester_pubkey}`.
  - [ ] Nostr event kinds: `Kind 31001` (Offer), `Kind 31002` (Bid), `Kind 31003` (Contract).
  - [ ] Matching engine: automatic pairing of bids and offers based on price, capability, and reputation.
  - [ ] Contract negotiation: 3-way handshake (Offer -> Bid -> Accept -> Execute).
- **Dependencies**: `agentmesh-core`, `agentmesh-relay`, `agentmesh-identity`
- **Estimated Complexity**: High
- **Target Version**: v4.1.0

#### Epic: Reputation Oracle
- **Description**: Web-of-Trust based reputation system to prevent Sybil attacks in the marketplace.
- **Acceptance Criteria**:
  - [ ] `ReputationOracle` class computing PageRank-like scores over the mesh trust graph.
  - [ ] Agents publish `TrustVote` events (+1 / -1) for peers they've interacted with.
  - [ ] Weighted aggregation: votes from high-reputation agents count more.
  - [ ] API: `oracle.get_score(agent_pubkey) -> float`.
  - [ ] Integration with `MarketplaceAgent`: reject offers from agents with score < threshold.
- **Dependencies**: `agentmesh-core`, `agentmesh-relay`, `agentmesh-identity`
- **Estimated Complexity**: High
- **Target Version**: v4.1.0

#### Epic: Micropayments Layer
- **Description**: Lightning Network and Cashu ecash integration for agent-to-agent payments.
- **Acceptance Criteria**:
  - [ ] `PaymentAgent` supporting Lightning invoices (BOLT11) via `lndgrpc` or `cln-grpc`.
  - [ ] Cashu token minting and redemption for offline-capable payments.
  - [ ] `EscrowAgent`: holds payments in 2-of-2 multisig until task completion is verified.
  - [ ] Auto-payment on successful task delivery (triggered by marketplace contract).
  - [ ] Payment receipts stored on IPFS via `agentmesh-vault` for audit trail.
- **Dependencies**: `agentmesh-core`, `agentmesh-vault`, `agentmesh-relay`
- **Estimated Complexity**: Very High
- **Target Version**: v4.2.0

---

### Milestone 3: Infrastructure & UX

Goal: Make the mesh accessible to non-technical users and compatible with industry standards.

#### Epic: MCP Native Hub
- **Description**: Full Model Context Protocol (MCP) integration, making AgentMesh an MCP server and client.
- **Acceptance Criteria**:
  - [ ] `MCPHubAgent` implementing the MCP server spec (stdio and SSE transports).
  - [ ] Expose mesh capabilities as MCP tools: `query_agent`, `store_memory`, `send_message`.
  - [ ] MCP client mode: AgentMesh agents can call external MCP servers.
  - [ ] Tool discovery: auto-register Nostr agent capabilities as MCP tools.
  - [ ] Authentication: Nostr NIP-44 encrypted MCP sessions.
- **Dependencies**: `agentmesh-core`, `agentmesh-pro` (orchestrator), `mcp` SDK
- **Estimated Complexity**: High
- **Target Version**: v4.0.0

#### Epic: Mesh Dashboard
- **Description**: Real-time web visualization of the P2P mesh network.
- **Acceptance Criteria**:
  - [ ] WebSocket endpoint streaming mesh events (agent joins, message flows, capability updates).
  - [ ] D3.js / Cytoscape.js force-directed graph showing agents as nodes, trust relationships as edges.
  - [ ] Live metrics: message throughput, agent uptime, reputation scores, payment volume.
  - [ ] Filterable views: by capability, by reputation tier, by geographic relay.
  - [ ] Mobile-responsive design using Tailwind + HTMX.
- **Dependencies**: `agentmesh-core`, `agentmesh-relay`, `agentmesh-studio`
- **Estimated Complexity**: Medium
- **Target Version**: v4.0.0

#### Epic: Mobile Node
- **Description**: Lightweight agent runtime for Android/iOS capable of joining the mesh.
- **Acceptance Criteria**:
  - [ ] Python runtime packaged with `BeeWare` or `Kivy` for cross-platform mobile.
  - [ ] Reduced feature set: only `BaseAgent`, `NostrAgent`, and `VaultAgent`.
  - [ ] Background Nostr relay connection with push notification bridge.
  - [ ] Battery-optimized: batch event processing, adaptive sync intervals.
  - [ ] QR-code based onboarding: scan to import Nostr nsec and join default relays.
- **Dependencies**: `agentmesh-core`, `agentmesh-relay`, `agentmesh-vault`
- **Estimated Complexity**: Very High
- **Target Version**: v4.3.0

---

### v4.0 Release Timeline

| Version | Milestone | Target Date | Key Deliverables |
|---|---|---|---|
| v4.0.0-alpha | Identity & Discovery | Q4 2026 | `agentmesh-identity`, Capability Crawler, Federated Search |
| v4.0.0-beta | MCP & Dashboard | Q1 2027 | MCP Hub, Mesh Dashboard WebUI |
| v4.0.0 | Stable v4.0 | Q1 2027 | All alpha+beta features stable, docs complete |
| v4.1.0 | Marketplace Core | Q2 2027 | Marketplace Agent, Reputation Oracle |
| v4.2.0 | Payments | Q3 2027 | Lightning + Cashu integration, EscrowAgent |
| v4.3.0 | Mobile | Q4 2027 | Mobile Node MVP |

---

## Contributing

We welcome contributions. Please open an issue to discuss your plan before starting.
Every feature should follow the async-first pattern and include tests.
