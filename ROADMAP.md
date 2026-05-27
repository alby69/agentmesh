# Roadmap — Web App Podcast Generator

## Visione

Interfaccia web dove l'utente incolla l'URL di una newsletter, vede l'elenco degli articoli con descrizione, seleziona quelli che vuole e genera file audio MP3 con un click.

```
Incolla URL newsletter
        │
        ▼
┌──────────────────────────────┐
│  Elenco articoli trovati:    │
│                              │
│  ☑ AI Framework XYZ lancia  │
│     nuova versione 5.0       │
│  ☑ OpenAI annuncia GPT-5    │
│  ☑ Nuovo tool per MLops     │
│     ...                      │
│                              │
│  [Seleziona tutti]  [Genera] │
└──────────────────────────────┘
        │
        ▼
   Download MP3 pronto
```

## Stack consigliato

### Backend: **FastAPI** (Python)
- Stesso linguaggio del progetto, riusa `src/builder.py` e tutti i moduli esistenti
- Async nativo (compatibile with `edge-tts`, `playwright`)
- Documentazione automatica OpenAPI
- Built-in validazione Pydantic (compatibile con le dataclass esistenti)

### Database: **SQLite + SQLModel**
- Zero configurazione, file-based, perfetto per deploy singolo utente
- SQLModel = Pydantic + SQLAlchemy, typing forte
- Per salvare: cronologia episodi, preferenze utente, newsletter processate
- In futuro si scala a PostgreSQL se serve multi-utente

### Frontend: **FastHTML** (consigliato) **oppure** HTMX + Jinja2

**Opzione A — FastHTML (Answer.AI)**
- Framework Python puro per HTML reattivo
- Server-side rendering, niente JavaScript
- Unico file Python per tutta la UI
- Perfetto per app monouso/small team

**Opzione B — HTMX + Jinja2 + Tailwind** (più flessibile)
- HTMX per interattività senza scrivere JS
- Jinja2 template (già incluso in FastAPI)
- Tailwind CSS per UI accattivante
- Più controllabile se l'app cresce

### Per iniziare subito: **Gradio**
- Ancora più veloce: una griglia di checkbox + pulsante
- Componenti UI già pronti, stile Hugging Face
- Meno bello esteticamente, ma funzionale in 20 righe

## Architettura Web

```
┌──────────┐     ┌──────────────────────────────────────┐
│  Browser │────▶│  FastAPI /src/web/                    │
│  (HTMX)  │     │                                      │
└──────────┘     │  GET / → form inserimento URL        │
                 │  POST /fetch → estrai articoli        │
                 │  POST /generate → seleziona + genera  │
                 │  GET /download/{id} → scarica MP3    │
                 │                                      │
                 │  /src/builder.py (riusato!)           │
                 │  /src/fetcher.py                      │
                 │  /src/translator.py                   │
                 │  /src/tts.py                          │
                 │  /src/tracker.py                      │
                 │  /src/audio.py                        │
                 └──────────────────────────────────────┘
                              │
                     ┌───────▼────────┐
                     │  podcast.db    │
                     │  SQLite        │
                     └────────────────┘
```

## Tabella di marcia

### Fase 1 — Setup web (COMPLETATA ✅)
- [x] Installare FastAPI + uvicorn + SQLModel
- [x] Creare `src/web/` con struttura base
- [x] Spostare logica di estrazione articoli (oggi `fetcher.py` prende tutto il body, serve estrarre singoli articoli con titolo e descrizione)
- [x] Esporre endpoint `POST /fetch-articles` che accetta URL, estrai lista articoli
- [x] Template HTML minimale: form URL + lista risultati

### Fase 2 — Selezione e generazione (COMPLETATA ✅)
- [x] Endpoint `POST /generate` che accetta URL articolo + voce TTS
- [x] Feedback progresso (SSE o polling)
- [x] Download file MP3 generato
- [x] Salvataggio cronologia in SQLite

### Fase 3 — UX accattivante (COMPLETATA ✅)
- [x] Tailwind CSS per UI moderna
- [x] Preview testo tradotto prima di generare audio (Integrazione parziale via script .txt)
- [x] Player audio embedded per ascoltare prima di scaricare
- [x] Stato "in elaborazione" con spinner

### Fase 4 — Selezione multipla e playlist (COMPLETATA ✅)
- [x] Seleziona/deseleziona articoli individuali
- [x] Selzione "tutti" / "nessuno"
- [x] Generazione audio multipla in batch
- [x] Unione playlist → singolo MP3 (riusa `merge_audio_files`)

### Fase 5 — Polish (IN CORSO 🏗️)
- [ ] Autenticazione base (password single-user)
- [x] Deploy Docker
- [ ] Supporto multi-lingua (altre voci Edge-TTS)
- [ ] Ricerca e filtro cronologia
- [ ] Esportazione RSS per podcast player (Apple/Spotify)

## Cambiamenti necessari al codice esistente

1. **`src/fetcher.py`** — Aggiunta funzione `get_article_list` che estrae titoli e URL. ✅
2. **`src/builder.py`** — Refactoring completato per separare logica e UI. ✅
3. **Audio** — Integrazione sigle e merge completata. ✅
