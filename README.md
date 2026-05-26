# Podcast Generator

Pipeline automatica che trasforma newsletter in episodi podcast in **italiano**, pronti da ascoltare.

La sorgente delle news è completamente configurabile via `.env`: puoi usare qualsiasi newsletter ospitata su **Beehiiv** (o adattare lo scraper ad altre piattaforme modificando i selettori CSS).

## 🚀 Novità: Interfaccia Web

Oltre alla CLI, ora puoi usare la **Web App** per selezionare visivamente gli articoli che ti interessano e generare il tuo podcast personalizzato.

### Come avviare la Web App
```bash
# Installa le dipendenze aggiuntive
pip install -r requirements.txt

# Avvia il server
uvicorn src.web.app:app --reload
```
Poi apri `http://localhost:8000` nel tuo browser.

---

## Architettura

```
Newsletter (sorgente configurabile)
       │
       ▼
  ┌───────────┐
  │  Fetcher  │  Playwright → estrae titolo + contenuto dalla pagina archive
  └─────┬─────┘
        │
        ▼
  ┌───────────┐
  │ Translator│  Google Gemini → traduce e riscrive in italiano + Web Search Grounding
  └─────┬─────┘
        │
        ▼
  ┌───────────┐
  │    TTS    │  ElevenLabs o Edge-TTS → genera audio MP3 con voce naturale
  └─────┬─────┘
        │
        ▼
  ┌───────────┐
  │  Audio    │  pydub → verifica durata, aggiunge sigle, unisce file
  └───────────┘
```

Il progetto è strutturato su tre livelli:

1. **Servizi** (`src/fetcher.py`, `translator.py`, `tts.py`, `audio.py`, `tracker.py`) — moduli puri, ognuno con una sola responsabilità
2. **Builder** (`src/builder.py`) — layer async che orchesta i servizi, senza dipendenze CLI. Importabile da web app o altri frontend
3. **Pipeline CLI** (`src/pipeline.py` + `main.py`) — thin wrapper con progress bar Rich, chiama il builder

## Requisiti

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) (necessario per l'elaborazione audio)
- [Playwright browsers](https://playwright.dev/python/docs/installation) (`playwright install firefox`)
- Chiave API **Google Gemini** ([AI Studio](https://aistudio.google.com/)) — gratuita, generosissima
- **Edge-TTS** non richiede chiave API (gratuito, nessun limite di token)
- **ElevenLabs** (opzionale, richiede API KEY)

## Installazione

```bash
# Clona il repository
git clone <url> && cd podcast-generator

# Crea ambiente virtuale
python3 -m venv .venv && source .venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Installa il browser Playwright (Firefox)
playwright install firefox

# Configura le API key
cp .env.example .env
# modifica .env con la tua GEMINI_API_KEY e la sorgente newsletter
```

### File `.env`

```
# === API ===
GEMINI_API_KEY=your_gemini_api_key_here
# Opzionale: se presente attiva ElevenLabs, altrimenti usa Edge-TTS gratuito
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# === Sorgente newsletter (almeno NEWSLETTER_URL o ARCHIVE_URL) ===
SOURCE_NAME=There's An AI For That
NEWSLETTER_URL=https://newsletter.theresanaiforthat.com
# ARCHIVE_URL=https://newsletter.theresanaiforthat.com/archive

# === Selettori scraping (default Beehiiv) ===
LOAD_MORE_SELECTOR=button:has-text('Load More'), a:has-text('Load More')
LINK_PATTERN=/p/

# === Sigle (Percorsi file MP3) ===
INTRO_PATH=./assets/intro.mp3
OUTRO_PATH=./assets/outro.mp3

# === Opzionali ===
TTS_VOICE=it-IT-GiuseppeNeural  # Edge: it-IT-GiuseppeNeural, ElevenLabs: ID voce
GEMINI_MODEL=gemini-3.5-flash
MAX_EPISODE_MINUTES=60
OUTPUT_DIR=./output
USE_WEB_SEARCH=true
```

### Configurazione della sorgente

| Variabile | Obbligatoria | Default | Descrizione |
|-----------|:---:|:-------:|-------------|
| `SOURCE_NAME` | No | `newsletter` | Nome visualizzato della fonte |
| `NEWSLETTER_URL` | No* | — | URL base della newsletter |
| `ARCHIVE_URL` | No* | `{NEWSLETTER_URL}/archive` | URL completo della pagina archive |
| `LOAD_MORE_SELECTOR` | No | `button:has-text('Load More'), a:has-text('Load More')` | Selettore CSS per il pulsante "Load More" |
| `LINK_PATTERN` | No | `/p/` | Pattern URL per filtrare i link ai singoli post |

\* Almeno uno tra `NEWSLETTER_URL` e `ARCHIVE_URL` deve essere impostato.

> **Nota:** Lo scraper è ottimizzato per **Beehiiv**. Per altre piattaforme, modifica `LOAD_MORE_SELECTOR` e `LINK_PATTERN`.

## Utilizzo CLI

```bash
# Episodio giornaliero: ultima newsletter → traduzione → audio
python3 main.py daily
python3 main.py daily --search            # con approfondimento Google Search

# Episodio settimanale: aggrega N newsletter in una compilation
python3 main.py weekly --days 7

# BACKFILL: scarica TUTTE le newsletter passate non ancora processate
python3 main.py fetch-all --limit 10

# Verifica lo stato del tracker
python3 main.py status
```

## Funzionalità Avanzate

### 🔍 Web Search Grounding
Usa il flag `--search` (o imposta `USE_WEB_SEARCH=true` nel `.env`) per permettere a Gemini di usare Google Search per approfondire le notizie della newsletter con dati tecnici e curiosità aggiornate.

### 🎵 Sigle Intro/Outro
Puoi aggiungere automaticamente una sigla iniziale e finale ai tuoi episodi impostando `INTRO_PATH` e `OUTRO_PATH` nel tuo file `.env`.

### 🐳 Docker
Il progetto include un `Dockerfile` pronto per il deploy containerizzato:
```bash
docker build -t podcast-generator .
docker run -p 8000:8000 --env-file .env podcast-generator
```

## Struttura del progetto

```
├── main.py                  # CLI (Typer) — entrypoint, chiama asyncio.run()
├── src/
│   ├── __init__.py          # Esporta classi e funzioni principali
│   ├── config.py            # Config dataclass, validazione, .env
│   ├── models.py            # Dataclass condivisi (Newsletter, Episode)
│   ├── fetcher.py           # Scraping della newsletter con Playwright
│   ├── translator.py        # Traduzione/riscrittura con Gemini
│   ├── tts.py               # Text-to-Speech (Edge-TTS o ElevenLabs)
│   ├── audio.py             # Utilità audio (durata, intro/outro, merge)
│   ├── tracker.py           # Tracker JSON per evitare duplicati
│   ├── builder.py           # Async orchestration layer (no CLI deps)
│   ├── pipeline.py          # Thin wrapper CLI con Rich progress bar
│   └── web/                 # Web App (FastAPI + HTMX + Tailwind)
├── output/
│   ├── daily/               # Puntate giornaliere (MP3 + script TXT)
│   ├── weekly/              # Compilation settimanali
│   └── .processed.json      # Tracker
├── .env
├── requirements.txt
└── README.md
```

## Stack

| Componente | Tecnologia | Costo |
|------------|-----------|-------|
| Web UI | FastAPI + HTMX + Tailwind | Gratuito |
| Scraping | Playwright (Firefox) | Gratuito |
| LLM | Google Gemini 3.5 Flash | Gratuito (free tier) |
| TTS | Edge-TTS / ElevenLabs | Gratuito / Freemium |
| Database | SQLite + SQLModel | Gratuito |
| Audio | pydub + FFmpeg | Gratuito |
| CLI | Typer + Rich | Gratuito |
