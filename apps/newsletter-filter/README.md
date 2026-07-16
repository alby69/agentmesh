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

## Quick Start

```bash
# 1. Installa le dipendenze
uv sync --package newsletter-filter

# 2. Configura
cp apps/newsletter-filter/.env.example apps/newsletter-filter/.env
# Compila .env con le tue credenziali LLM e sorgenti

# 3. Avvia la Web UI
cd apps/newsletter-filter
uv run uvicorn newsletter_filter.web.app:app --reload --port 8000

# 4. Oppure usa la CLI
uv run python apps/newsletter-filter/main.py --source-type rss --query "AI e HR"
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
│   ├── agents/
│   │   └── filter_agent.py              # FilterAgent (BaseAgent + LLM)
│   └── web/
│       ├── app.py                       # FastAPI server + routes
│       ├── db.py                        # SQLite (articles, settings, scan_jobs)
│       └── templates/                   # Jinja2 + Tailwind + HTMX
│           ├── base.html
│           ├── index.html
│           ├── articles_table.html
│           └── settings.html
└── tests/
    └── test_filter.py                   # 6 test (pytest + asyncio)
```

## CLI

```bash
# RSS con query personalizzata
python main.py --source-type rss --source "https://stefanogatti.substack.com/feed" --query "HR e AI"

# IMAP
python main.py --source-type imap --source "INBOX" --limit 10

# Output JSON
python main.py --source-type rss --output json
```

### Opzioni

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--source-type` | `rss` | Tipo sorgente: `rss` o `imap` |
| `--source` | da config | URL RSS o cartella IMAP |
| `--query` | da config | Criteri di ricerca semantica |
| `--limit` | `5` | Numero massimo di articoli |
| `--output` | `text` | Formato output: `text` o `json` |

## Web UI

La web UI espone:

| Route | Metodo | Descrizione |
|-------|--------|-------------|
| `/` | GET | Dashboard con statistiche e tabella articoli |
| `/scan` | POST | Avvia scansione (background task) |
| `/scan-status/{id}` | GET | Stato scansione (HTMX polling) |
| `/articles` | GET | Lista articoli (parziale HTMX) |
| `/settings` | GET/POST | Gestione impostazioni |
| `/clear` | POST | Cancella tutti gli articoli |
| `/api/articles` | GET | API JSON articoli |
| `/api/stats` | GET | API JSON statistiche |

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
- **Build**: hatchling, uv workspace
