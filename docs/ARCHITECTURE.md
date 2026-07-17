# AgentMesh: Technical Architecture

AgentMesh adopts a layered architecture to separate responsibilities, ensure maximum decentralization, and enable an autonomous agentic economy.

## 1. Network Layer (P2P Mesh)
The physical and logical foundation of the system.
- **Technology**: Nostr (NIP-01, NIP-04, NIP-94).
- **Role**: Peer discovery, NAT traversal (via relays), encrypted event transport.
- **Evolution**: Investigating `libp2p` for pure gossip mesh communications in scenarios where Nostr relays are insufficient.

## 2. Storage Layer (Distributed Storage)
The long-term memory of the mesh.
- **Technology**: IPFS (InterPlanetary File System).
- **Role**: Content-addressed storage. Every file (audio, script, metadata) is identified by a CID (Content Identifier).
- **Deduplication**: If multiple agents generate the same content, the space occupied on the network does not increase.

## 3. Coordination & Discovery Layer (v3.0 Core)
The nervous system that coordinates agents and allows the discovery of new capabilities.

### Agent Registry (v3.0.1)
Decentralized discovery via Nostr. Agents publish an `AgentCapability` event to allow discovery of specialized skills:
```json
{
    "agent_id": "unique-id",
    "name": "TTS Agent",
    "description": "High-quality Italian voice synthesis",
    "version": "1.0.0",
    "public_key": "npub...",
    "capabilities": ["tts", "audio-processing"]
}
```

### AgentMessage Protocol (v3.0.2)
Standardized inter-agent communication:
```json
{
    "id": "msg-uuid",
    "sender": "npub-sender",
    "receiver": "npub-receiver",
    "type": "task",
    "payload": {
        "action": "generate_audio",
        "params": { ... }
    },
    "timestamp": 1234567890
}
```

## 4. Incentives & Payments Layer (Value Transfer)
Enables peer-to-peer economy between agents (A2A) and between users and agents.
- **Technology**: **Lightning Network** + **Cashu** (ecash).
- **Role**: Micropayments for tasks.
- **Model**: Pay-per-request (A2A).

## 5. Agent Layer (Autonomous Workers)
Where logic resides.
- **Task Agent (v3.0.3)**: High-level orchestrator.
- **Workflow Agent (v3.5)**: Complex sequence manager.
- **Project Agent (v4.0)**: Goal-oriented autonomous project representative.

## 6. Infrastructure & Tooling
Helper libraries and shared infrastructure components.
- **AgentMesh LLM**: Unified provider interface for Gemini, OpenAI, Anthropic, and Ollama.
- **Mesh Config**: Specialized, decoupled configuration management for apps and agents.

## 7. Application Structure
Every app in the monorepo follows a standardized template (`scripts/new-app.sh`):

```
apps/{app-name}/
├── pyproject.toml           # Dependencies, build config, workspace sources
├── main.py                  # argparse CLI entry point (--server, --port, --host)
├── README.md
├── .env.example             # Environment variable template
├── .gitignore               # data/, *.db, output/, .env
├── {app_name}/
│   ├── __init__.py          # __version__
│   ├── config.py            # Pydantic BaseSettings with env_prefix
│   ├── agents/              # Agent implementations (BaseAgent subclasses)
│   ├── web/
│   │   ├── app.py           # FastAPI with lifespan manager
│   │   ├── db.py            # SQLite with WAL mode, data/ directory
│   │   └── templates/       # Jinja2 + Tailwind CSS + HTMX
│   └── data/                # Runtime database (gitignored)
└── tests/
    ├── conftest.py          # Shared fixtures (temp DB per test)
    └── test_*.py
```

**Conventions:**
- **CLI**: `argparse` (stdlib), no external CLI framework
- **Config**: `pydantic-settings` `BaseSettings` with `env_file=".env"` and `extra="ignore"`
- **Web**: FastAPI + Jinja2Templates + Tailwind CDN + HTMX
- **Database**: Raw `sqlite3` with WAL mode, `data/` directory, env-overridable path
- **Tests**: `pytest` + `unittest.mock`, `TestClient` for web, temp DB in `tmp_path`
- **Nostr integration**: Via `agentmesh-relay` (`NostrAgent` base class)
- **LLM integration**: Via `agentmesh-llm` (`LLMProviderFactory`)

---

## Technical Directives
1. **Async First**: All I/O and inter-agent communication must be asynchronous.
2. **Modular Identity**: Agents must be able to swap identities (keys) and remain functional.
3. **P2P Fallback**: Systems must remain partially functional even if specific relays go down.
4. **Standardized Structure**: All apps use the same template, CLI pattern, and config approach.
