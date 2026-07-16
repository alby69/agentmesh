# ROADMAP — Newsletter Filter & Extraction App

Piano di sviluppo in più fasi per l'applicazione di filtraggio cognitivo di newsletter e feed, integrata nel monorepo AgentMesh.

---

## Fase 1: Core Filtering Agent & Extraction Engine ✅ COMPLETATA

Sviluppo del modulo applicativo asincrono `apps/newsletter-filter`, completamente autonomo e disaccoppiato dal core del framework.

### 1.1 Struttura del Pacchetto ✅
- [x] `pyproject.toml` con dipendenze workspace e third-party
- [x] Package `newsletter_filter/` con moduli: `config.py`, `engine.py`, `fetcher.py`
- [x] Sottopackage `agents/` con `FilterAgent`
- [x] Entry point CLI `main.py`
- [x] Test suite in `tests/`

### 1.2 Configurazione (config.py) ✅
- [x] Pydantic `BaseSettings` con override da env vars
- [x] Settings LLM (provider, api_key, model)
- [x] Settings IMAP (host, user, password, folder)
- [x] Settings RSS (lista URL)
- [x] Default query semantica

### 1.3 Fetcher (fetcher.py) ✅
- [x] `ArticleItem` data class con `to_dict()`
- [x] `fetch_rss()` con feedparser + trafilatura (3 livelli di fallback)
- [x] `fetch_imap()` con imap-tools + trafilatura
- [x] Gestione errori e logging

### 1.4 FilterAgent (agents/filter_agent.py) ✅
- [x] `FilterAgentConfig` estende `MeshConfig`
- [x] `FilterAgent` estende `BaseAgent`
- [x] Lifecycle: `start()` / `stop()`
- [x] `handle_message()` per messaggi tipo `"task"`
- [x] `filter_and_extract()` con prompt LLM e parsing JSON
- [x] Fallback heuristic keyword-matching on LLM failure

### 1.5 Engine (engine.py) ✅
- [x] `process_filtering()` orchestratore async
- [x] Routing rss/imap
- [x] Costruzione `AgentMessage` standardizzate
- [x] Gestione errori per-articolo

### 1.6 CLI (main.py) ✅
- [x] Argparse con `--source-type`, `--source`, `--query`, `--limit`
- [x] Inizializzazione LLM via `LLMProviderFactory`
- [x] Report formattato con colori

### 1.7 Test (tests/test_filter.py) ✅
- [x] Test `ArticleItem.to_dict()`
- [x] Test `fetch_rss` mockato
- [x] Test `fetch_imap` mockato
- [x] Test `filter_and_extract` mock LLM
- [x] Test `handle_message` con AgentMessage
- [x] Test `process_filtering` end-to-end mockato

---

## Fase 1+: Robustezza e Qualità ✅ COMPLETATA

Miglioramenti alla Fase 1 per portare l'app a livello production-ready.

### 1.8 Pulizia dipendenze ✅
- [x] Rimuovere `agentmesh-relay`, `agentmesh-vault` da pyproject.toml (non utilizzati)
- [x] Rimuovere `playwright` (non utilizzato)
- [x] Mantenere `fastapi` + `uvicorn` + `jinja2` (servono per Fase 2)
- [x] Aggiungere `python-multipart` (necessario per form POST FastAPI)

### 1.9 File di esempio ✅
- [x] Creare `.env.example` con tutti i parametri documentati

### 1.10 Parallel processing ✅
- [x] Convertire l'elenco sequenziale in `engine.py` a `asyncio.gather` con semaforo
- [x] Configurare concorrenza massima (default: 3 chiamate LLM in parallelo)

### 1.11 Miglioramento fallback ✅
- [x] Keyword matching più robusto: frasi multiword, lowercasing, filtro stop-word
- [x] Score fallback proporzionale al numero di keyword matchate
- [x] Metodo `_extract_keywords()` per parsing keyword da query

### 1.12 Output opzioni ✅
- [x] Flag `--output json` per output JSON strutturato

---

## Fase 2: Integrazione UI & Workflow ✅ COMPLETATA

Web UI interattiva con FastAPI + HTMX per gestione sorgenti, keyword e visualizzazione risultati.

### 2.1 Web Server (FastAPI) ✅
- [x] Modulo `newsletter_filter/web/` con `app.py`, `db.py`
- [x] Route principali: `/`, `/scan`, `/settings`, `/articles`, `/clear`
- [x] API REST: `/api/articles`, `/api/stats`
- [x] Templates Jinja2 in `web/templates/`

### 2.2 Dashboard ✅
- [x] Pagina principale con tabella articoli filtrati
- [x] Indicatore rilevanza (verde/rosso) per ogni articolo
- [x] Riepilogo statistiche: totali, rilevanti, ultima scansione
- [x] Pulsante "Avvia scansione" con HTMX polling
- [x] Filtro "Solo Rilevanti" e pulsante "Pulisci"

### 2.3 Pannello Impostazioni ✅
- [x] Form per configurare sorgenti RSS
- [x] Form per configurare credenziali IMAP
- [x] Form per definire query e keyword di ricerca
- [x] Form per selezionare provider e modello LLM

### 2.4 Pipeline Asincrona ✅
- [x] Background task per scansione (`asyncio.create_task`)
- [x] Stato scansione in tempo reale via HTMX polling (`/scan-status/{job_id}`)
- [x] Tabella storico scansioni recenti

### 2.5 Persistenza ✅
- [x] Database SQLite per storage articoli e settings
- [x] Tabella `articles` con: title, url, date, content, score, relevant, summary, key_points, justification
- [x] Tabella `settings` con: key, value
- [x] Tabella `scan_jobs` per tracciamento scansioni
- [x] Deduplication per URL (`INSERT OR REPLACE`)

---

## Fase 3: Mesh Automation & A2A Economy ⬜

Integrazione con il protocollo AgentMesh per automazione distribuita e micropagamenti.

### 3.1 Nostr Relay Integration ⬜
- [ ] Registrazione del FilterAgent sulla rete Nostr via `agentmesh-relay`
- [ ] Pubblicazione risultati come eventi Nostr
- [ ] Ricezione task da altri agenti sulla rete

### 3.2 Schedulazione Automatica ⬜
- [ ] Integrazione APScheduler per cron job
- [ ] Configurazione intervallo scansione (es. ogni 6 ore)
- [ ] Notifiche su nuovi articoli rilevanti

### 3.3 Vault Integration ⬜
- [ ] Storage credenziali IMAP encriptate via `agentmesh-vault`
- [ ] Rotazione automatica chiavi

### 3.4 Micropagamenti ⬜
- [ ] Abilitazione query a pagamento via Lightning/Cashu
- [ ] Rate limiting basato su credito
- [ ] Dashboard economico per consumi

---

## Note Architetturali

### Principio di Disaccoppiamento
- **Framework (`packages/`)**: Fornisce mattoni fondamentali e protocolli generici
- **Applicazione (`apps/newsletter-filter`)**: Implementa logica di business specifica
- Comunicazione unicamente tramite interfacce standardizzate (`agentmesh-core`, `agentmesh-llm`)

### Stack Tecnologico
- **Backend**: Python 3.10+, async/await, Pydantic v2
- **LLM**: Via `agentmesh-llm` (OpenAI, Anthropic, Gemini, Ollama)
- **Web**: FastAPI + HTMX + Jinja2
- **Fetch**: feedparser, trafilatura, imap-tools
- **Test**: pytest, pytest-asyncio, unittest.mock
- **Build**: hatchling, uv workspace
