# Newsletter Filter & Extraction App

Applicazione cognitiva per il filtraggio di newsletter ed estrazione di contenuti rilevanti, integrata nel monorepo [AgentMesh](https://github.com/alby69/agentmesh).

## Funzionalità

- **RSS Feed Reader**: Lettura e parsing di feed RSS pubblici con `feedparser` + `trafilatura`
- **IMAP Client**: Scaricamento e parsing di email da qualsiasi casella di posta (Gmail, Substack, ecc.)
- **FilterAgent cognitivo**: Analisi semantica dei contenuti via LLM (`agentmesh-llm`) con scoring di rilevanza
- **Fallback intelligente**: Keyword-matching proporzionale quando il LLM non è disponibile
- **Parallel processing**: Elaborazione concorrente degli articoli con `asyncio.gather` (max 3 worker)
- **Web UI**: Dashboard interattiva FastAPI + HTMX per avviare scansioni, visualizzare risultati e gestire le impostazioni
- **Persistenza**: Storage SQLite con deduplication per URL
- **CLI**: Interfaccia a riga di comando con output testuale o JSON
- **Auto-scan**: Scansioni RSS/IMAP automatiche ogni giorno via APScheduler (8:00 RSS, 9:00 IMAP)
- **Nostr Mesh**: Registrazione automatica dell'agente sulla rete Nostr (Kind 30311) e pubblicazione articoli (Kind 29001)
- **A2A Economy**: API REST per agenti esterni con micropagamenti Cashu/Lightning

## Quick Start

```bash
# 1. Installa le dipendenze
uv sync --package newsletter-filter

# 2. Configura
cp apps/newsletter-filter/.env.example apps/newsletter-filter/.env
# Compila .env con le tue credenziali LLM e sorgenti

# 3. Avvia la Web UI
PYTHONPATH=apps/newsletter-filter uv run python apps/newsletter-filter/main.py --server --port 8001

# 4. Avvia in modalita daemon (server + scheduler + mesh)
PYTHONPATH=apps/newsletter-filter uv run python apps/newsletter-filter/main.py --daemon --port 8001

# 5. Oppure usa la CLI
PYTHONPATH=apps/newsletter-filter uv run python apps/newsletter-filter/main.py --source-type rss --query "AI e HR"
```

## Struttura

```
apps/newsletter-filter/
├── main.py                              # CLI entry point
├── pyproject.toml                       # Dipendenze e configurazione build
├── .env.example                         # Template configurazione
├── ROADMAP.md                           # Piano di sviluppo in fasi
├── newsletter_filter/
│   ├── config.py                        # Pydantic Settings (env vars)
│   ├── engine.py                        # Orchestratore pipeline async
│   ├── fetcher.py                       # Fetch RSS e IMAP
│   ├── scheduler.py                     # APScheduler per auto-scan periodico
│   ├── mesh.py                          # Nostr mesh agent + A2A economy
│   ├── agents/
│   │   └── filter_agent.py              # FilterAgent (BaseAgent + LLM)
│   └── web/
│       ├── app.py                       # FastAPI server + routes + A2A API
│       ├── db.py                        # SQLite (articles, settings)
│       └── templates/                   # Jinja2 + Tailwind + HTMX
└── tests/
    ├── test_filter.py                   # Test FilterAgent e pipeline
    └── test_web.py                      # Test web routes e DB
```

## CLI

```bash
# RSS con query personalizzata
python main.py --source-type rss --source "https://stefanogatti.substack.com/feed" --query "HR e AI"

# IMAP
python main.py --source-type imap --source "INBOX" --limit 10

# Output JSON
python main.py --source-type rss --output json

# Modalita daemon (server + scheduler + mesh)
python main.py --daemon --port 8001
```

### Opzioni

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--server` | `false` | Avvia solo la web UI |
| `--daemon` | `false` | Avvia server + scheduler + mesh agent |
| `--port` | `8001` | Porta del server web |
| `--source-type` | `rss` | Tipo sorgente: `rss` o `imap` |
| `--source` | da config | URL RSS o cartella IMAP |
| `--query` | da config | Criteri di ricerca semantica |
| `--limit` | `5` | Numero massimo di articoli |
| `--output` | `text` | Formato output: `text` o `json` |

## Web UI

| Route | Metodo | Descrizione |
|-------|--------|-------------|
| `/` | GET | Dashboard con statistiche e tabella articoli |
| `/articles` | GET | Lista articoli (parziale HTMX) |
| `/article/{id}` | GET | Dettaglio articolo (modal) |
| `/trigger-scan` | POST | Avvia scansione (background task) |
| `/check-scan-status/{id}` | GET | Stato scansione (HTMX polling) |
| `/save-settings` | POST | Salva impostazioni |
| `/export-podcast` | POST | Invia articoli a Podcast Generator |

## A2A Economy API

API REST per agenti esterni che vogliono interrogare i contenuti filtrati.

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/v1/a2a/articles` | GET | Query articoli rilevanti (richiede `cashu_token`) |
| `/api/v1/a2a/pay` | GET | Registra micropagamento Cashu |
| `/api/v1/a2a/payments` | GET | Storico micropagamenti |
| `/api/v1/a2a/scan` | POST | Trigger scansione remota |
| `/api/v1/a2a/mesh/publish` | GET | Pubblica articoli su Nostr mesh |

### Esempio: query articoli da agente esterno

```bash
# Query articoli rilevanti con token Cashu
curl "http://localhost:8001/api/v1/a2a/articles?criteria=AI+HR&limit=5&cashu_token=abc123"
```

## Configurazione

Tutte le impostazioni sono gestite via variabili d'ambiente o file `.env`:

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `FILTER_LLM_PROVIDER` | `openai` | Provider LLM |
| `FILTER_LLM_API_KEY` | - | API key del provider |
| `FILTER_LLM_MODEL` | `gpt-4o-mini` | Modello LLM |
| `FILTER_RSS_URLS` | `[]` | Lista URL RSS |
| `FILTER_IMAP_HOST` | - | Host IMAP |
| `FILTER_IMAP_USER` | - | Utente IMAP |
| `FILTER_IMAP_PASSWORD` | - | Password IMAP |
| `FILTER_IMAP_FOLDER` | `INBOX` | Cartella IMAP |
| `FILTER_DEFAULT_QUERY` | `"Risorse Umane e AI..."` | Query semantica default |
| `FILTER_NOSTR_SECRET_KEY` | - | Chiave Nostr per mesh agent (auto-generata se assente) |

## Testing

```bash
# Esegui i test
uv run pytest apps/newsletter-filter/tests/ -v

# Lint
uv run ruff check apps/newsletter-filter/
```

## Stack

- **Backend**: Python 3.10+, async/await, Pydantic v2
- **LLM**: Via `agentmesh-llm` (OpenAI, Anthropic, Gemini, Ollama)
- **Web**: FastAPI + HTMX + Jinja2 + Tailwind CSS
- **Fetch**: feedparser, trafilatura, imap-tools
- **DB**: SQLite (WAL mode)
- **Mesh**: `agentmesh-relay` (Nostr P2P, Kind 29001/30311)
- **Scheduler**: APScheduler (cron-based periodic scans)
- **Build**: hatchling, uv workspace
