# `erpseed-agent` — Enterprise Resource Planning Agent for AgentMesh

`erpseed-agent` is a specialized autonomous agent and mesh gateway that integrates the **ERPSEED** low-code ERP platform into the **AgentMesh** ecosystem.

---

## 1. Overview & Architecture

Unlike passive HTTP bridges, `erpseed-agent` is a fully sovereign Nostr-native agent:
- **P2P Identity & Messaging (`agentmesh-relay`)**: Subclasses `NostrAgent` to communicate over Nostr relays using Kind `29001` (Encrypted Agent Messages) and Kind `30311` (Agent Registry Capability Advertising).
- **IPFS Vault Archiving (`agentmesh-vault`)**: Wraps `VaultAgent` via `ERPSeedVaultBridge` to archive generated FatturaPA 1.2 XML invoices and reports directly to IPFS, publishing NIP-94 metadata (Kind `1063`).
- **LLM Assistance & Low-Code AI Builder (`agentmesh-llm`)**: Integrates multi-provider LLMs (`OpenAI`, `Gemini`, `Anthropic`, `Ollama`) to generate SysModels, UI view layouts, and workflow rules.
- **Modular Sub-Agents**: Orchestrates specialized domain agents (`Sales`, `Purchases`, `Inventory`, `Accounting`, `HR`, `Manufacturing`, `CRM`, `FatturaElettronica`, `Workflow`, `AIBuilder`).
- **Dynamic API Capabilities**: Dynamically translates backend SysModels into CRUD capabilities (`data.<model>.list`, `data.<model>.create`, `data.<model>.get`, `data.<model>.update`, `data.<model>.delete`).
- **Web Operator Dashboard**: Provides a FastAPI + HTMX interface for tenant mapping, AI Builder, invoice inspection, workflow tracking, and IPFS vault operations.

---

## 2. Directory Structure

```
apps/erpseed-agent/
├── main.py                   # CLI entry point (--server, --sync-capabilities)
├── pyproject.toml            # Workspace dependencies (agentmesh-core, llm, relay, vault)
├── erpseed_agent/
│   ├── config.py             # ERPSeedConfig (Settings for Nostr, IPFS, LLM, ERPSEED)
│   ├── agents/
│   │   ├── erp_agent.py      # Main NostrAgent orchestrator & router
│   │   ├── base_module_agent.py # ERPModuleAgent base class
│   │   ├── sales_agent.py    # Sales orders, quotes, customer invoices
│   │   ├── purchase_agent.py # Procurement orders, supplier receipts
│   │   ├── inventory_agent.py# Warehouse stock movements, lot tracking
│   │   ├── accounting_agent.py # Prima Nota general ledger & VAT
│   │   ├── hr_agent.py       # Employees, attendance, payroll
│   │   ├── manufacturing_agent.py # BOM, production orders (ODP), MRP
│   │   ├── crm_agent.py      # Leads, opportunities, contracts
│   │   ├── fe_agent.py       # FatturaPA 1.2 XML & IPFS Vault store
│   │   ├── workflow_agent.py # Trigger-action rules & webhooks
│   │   ├── ai_builder_agent.py # Low-code AI model & view builder
│   │   └── policy_agent.py   # Governance overlay & ACLs
│   ├── bridge/
│   │   ├── executor.py       # HTTP client bridge to ERPSEED CQRS endpoints
│   │   ├── nostr_relay.py    # Nostr A2A event dispatcher & metadata publisher
│   │   ├── vault_bridge.py   # IPFS Vault document archiver
│   │   ├── tenant_resolver.py# SQLite mapping npub -> tenant_id
│   │   ├── capability_sync.py# Manifest sync from /api/v1/ai/capabilities
│   │   └── event_publisher.py# Domain event publisher
│   ├── llm/
│   │   ├── tools.py          # Low-code builder tool registry
│   │   └── builder_service.py# AI synthesis service using agentmesh-llm
│   └── web/
│       ├── app.py            # FastAPI dashboard server
│       ├── db.py             # SQLite persistence (tenants, capabilities, logs, invoices, workflows, vault)
│       └── templates/        # Tailwind CSS + HTMX templates
└── tests/                    # pytest suite
```

---

## 3. Running the Agent

### Start Web Operator Dashboard
```bash
python -m main --server --port 8000
```

### Manual Capability Sync
```bash
python -m main --sync-capabilities
```

---

## 4. Configuration Parameters

Set environment variables in `.env` or pass via environment:

| Variable | Description | Default |
|---|---|---|
| `ERPSEED_AGENT_ERPSEED_BASE_URL` | ERPSEED backend API base URL | `http://localhost:5000` |
| `ERPSEED_AGENT_NOSTR_RELAY_URL` | Primary Nostr Relay | `wss://relay.damus.io` |
| `ERPSEED_AGENT_NOSTR_PRIVATE_KEY` | Nostr Secret Key (nsec / hex) | (Auto-generated if empty) |
| `ERPSEED_AGENT_IPFS_GATEWAY_URL` | IPFS Gateway URL | `https://ipfs.io/ipfs/` |
| `ERPSEED_AGENT_IPFS_PROVIDER` | IPFS Provider (`mock`, `pinata`, `local`) | `mock` |
| `ERPSEED_AGENT_LLM_PROVIDER` | LLM Provider (`openai`, `gemini`, `anthropic`, `ollama`) | `openai` |
| `ERPSEED_AGENT_LLM_MODEL` | LLM Model Name | `gpt-4o-mini` |
