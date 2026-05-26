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

Il progetto è pensato per essere eseguito localmente via CLI, Web UI o schedulato con cron/systemd.

## Requisiti

- Python 3.12+
- [FFmpeg](https://ffmpeg.org/) (necessario per l'elaborazione audio)
- [Playwright browsers](https://playwright.dev/python/docs/installation) (`playwright install firefox`)
- Chiave API **Google Gemini** ([AI Studio](https://aistudio.google.com/)) — gratuita, generosissima
- Chiave API **ElevenLabs** ([ElevenLabs](https://elevenlabs.io/)) — opzionale (default: edge-tts gratuito)

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

# Configura le chiavi API
cp .env.example .env
# modifica .env con le tue chiavi e la sorgente newsletter
```

### File `.env`

```
# === API (obbligatorie) ===
GEMINI_API_KEY=your_gemini_api_key_here

# === Opzionali (ElevenLabs) ===
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=ErXwobaYiN019PkySvjV

# === Sigle (Percorsi file MP3) ===
INTRO_PATH=./assets/intro.mp3
OUTRO_PATH=./assets/outro.mp3

# === Configurazione ===
USE_WEB_SEARCH=true
GEMINI_MODEL=gemini-3.5-flash
OUTPUT_DIR=./output
```

## Utilizzo CLI

```bash
# Episodio giornaliero
python3 main.py daily
python3 main.py daily --search            # con approfondimento Google Search

# Episodio settimanale
python3 main.py weekly --days 7

# BACKFILL: processa tutto il pregresso
python3 main.py fetch-all --limit 10
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

## Stack

| Componente | Tecnologia | Costo |
|------------|-----------|-------|
| Web UI | FastAPI + HTMX + Tailwind | Gratuito |
| Scraping | Playwright (Firefox) | Gratuito |
| LLM | Google Gemini 3.5 Flash | Gratuito (free tier) |
| TTS | Edge-TTS / ElevenLabs | Gratuito / Freemium |
| Database | SQLite + SQLModel | Gratuito |
| Audio | pydub + FFmpeg | Gratuito |
