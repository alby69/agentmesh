# Podcast Generator — TAAFT

Pipeline automatica che trasforma le newsletter di [There's An AI For That](https://newsletter.theresanaiforthat.com/) in episodi podcast in **italiano**, pronti da ascoltare.

## Architettura

```
Newsletter (Beehiiv)
       │
       ▼
  ┌───────────┐
  │  Fetcher  │  Playwright → estrae titolo + contenuto dalla pagina archive
  └─────┬─────┘
        │
        ▼
  ┌───────────┐
  │ Translator│  Google Gemini → traduce e riscrive in italiano come script podcast
  └─────┬─────┘
        │
        ▼
  ┌───────────┐
  │    TTS    │  ElevenLabs → genera audio MP3 con voce naturale
  └─────┬─────┘
        │
        ▼
  ┌───────────┐
  │  Audio    │  pydub → verifica durata, aggiunge sigle, unisce file
  └───────────┘
```

Il progetto è pensato per essere eseguito localmente via CLI o schedulato con cron/systemd.

## Requisiti

- Python 3.12+
- [Playwright browsers](https://playwright.dev/python/docs/installation) (`playwright install firefox`)
- Chiave API **Google Gemini** ([AI Studio](https://aistudio.google.com/)) — gratuita, generosissima
- Chiave API **ElevenLabs** ([ElevenLabs](https://elevenlabs.io/)) — piano gratuito: 10.000 caratteri/mese

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
# modifica .env con le tue chiavi
```

### File `.env`

```
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM   # Rachel, cambia con una voce italiana
GEMINI_MODEL=gemini-2.5-flash
MAX_EPISODE_MINUTES=60
OUTPUT_DIR=./output
```

## Utilizzo

```bash
# Episodio giornaliero: ultima newsletter → traduzione → audio
python3 main.py daily

# Episodio settimanale: aggrega N newsletter in una compilation
python3 main.py weekly                    # ultime 7
python3 main.py weekly --days 14          # personalizza

# BACKFILL: scarica TUTTE le newsletter passate non ancora processate
python3 main.py fetch-all
python3 main.py fetch-all --limit 10      # prime 10 nuove
python3 main.py fetch-all --limit 50      # prime 50 nuove

# Verifica lo stato del tracker
python3 main.py status
```

### Comportamento di `fetch-all`

Il comando `fetch-all`:

1. **Scarica l'archivio completo** della newsletter (con paginazione automatica "Load More")
2. **Confronta** ogni newsletter con il file `output/.processed.json` (il tracker)
3. **Salta** quelle già processate (rilevamento duplicati via URL)
4. **Genera** una puntata MP3 giornaliera per ogni nuova newsletter in `output/daily/`
5. **Unisce** le puntate giornaliere in compilation settimanali in `output/weekly/`

## Struttura del progetto

```
├── main.py                  # CLI (Typer) — entrypoint
├── src/
│   ├── __init__.py          # Esporta classi e funzioni principali
│   ├── config.py            # Config dataclass, validazione, .env
│   ├── fetcher.py           # Scraping Beehiiv con Playwright
│   ├── translator.py        # Traduzione/riscrittura con Gemini
│   ├── tts.py               # Text-to-Speech con ElevenLabs
│   ├── audio.py             # Utilità audio (durata, intro/outro, merge)
│   ├── tracker.py           # Tracker JSON per evitare duplicati
│   └── pipeline.py          # Orchestrazione daily/weekly/fetch-all
├── output/
│   ├── daily/               # Puntate giornaliere (MP3 + script TXT)
│   │   ├── 2026-01-15_titolo_newsletter.mp3
│   │   ├── 2026-01-15_titolo_newsletter.txt
│   │   ├── 2026-01-16_titolo_newsletter.mp3
│   │   └── ...
│   ├── weekly/              # Compilation settimanali
│   │   ├── 2026-W03.mp3
│   │   ├── 2026-W04.mp3
│   │   └── ...
│   └── .processed.json      # Tracker (non modificare manualmente)
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Dettaglio fasi

### 1. Fetcher (`src/fetcher.py`)

Usa **Playwright** (Firefox headless) per navigare la pagina archive di Beehiiv, estrarre i link alle newsletter (`/p/...`) e scaricare il contenuto testuale di ciascuna, ripulendo script, stili e boilerplate.

- `fetch_latest_newsletter(archive_url) -> Newsletter` — ultima pubblicazione
- `fetch_multiple_newsletters(archive_url, count) -> list[Newsletter]` — ultime N

### 2. Translator (`src/translator.py`)

Invia il testo della newsletter a **Google Gemini** con un system prompt specializzato che chiede:

- traduzione accurata in italiano
- riscrittura in stile monologo podcast (colloquiale, dinamico, entusiasta)
- transizioni naturali tra gli argomenti
- aggregazione settimanale con macro-categorie (modalità weekly)

### 3. TTS (`src/tts.py`)

Invia lo script italiano a **ElevenLabs** usando `eleven_multilingual_v2` per una dizione perfetta in italiano, e salva l'output come MP3 (44100 Hz, 128 kbps).

### 4. Audio (`src/audio.py`)

Utility per:

- `check_duration()` — verifica che l'episodio non superi `MAX_EPISODE_MINUTES` (default: 60 min)
- `add_intro_outro()` — aggiunge sigla iniziale/finale (file MP3 opzionali)
- `merge_audio_files()` — unisce più file audio in uno

## Gestione della durata (limite 1 ora)

Una singola newsletter dura 5-8 minuti parlata. Per arrivare a ~1 ora:

| Opzione | Comando | Descrizione |
|---------|---------|-------------|
| **Settimanale** (consigliata) | `main.py weekly` | Aggrega 7 newsletter, Gemini le unisce per temi elimina duplicati → 30-45 minuti |
| **Quotidiana estesa** | (futuro) | Integra web search per approfondire ogni notizia |

## Voci ElevenLabs — Podcast maschili consigliate

⚠️ **Attenzione**: ElevenLabs ha cambiato la disponibilità delle voci via API. Sul **piano gratuito** solo poche voci funzionano. Le altre o non esistono più (404) o richiedono un abbonamento a pagamento (402).

## Modelli Gemini

| Modello | Uso | Costo |
|---------|-----|-------|
| `gemini-3.5-flash` ✅ IN USO | Traduzione e riscrittura podcast | Gratuito (free tier) |
| `gemini-3.1-flash-lite` | Alternativa più leggera e veloce | Gratuito (free tier) |
| `gemini-2.5-flash` | Versione precedente (default obsoleto) | Gratuito |

Per cambiare modello: aggiorna `GEMINI_MODEL` nel `.env`.

### Voci gratis che funzionano via API ✅

| Voce | Voice ID | Note |
|------|----------|------|
| **Antoni** ✅ IN USO | `ErXwobaYiN019PkySvjV` | Maschile, profonda e autorevole. Ideale per podcast |
| **Chris** | `iP95p4xoKVk53GoZ742B` | Maschile, tono medio e chiaro |
| **Daniel** | `onwK4e9ZLuTAKqWW03F9` | Maschile, caldo e fluido |

### Voci che richiedono abbonamento a pagamento 💳

| Voce | Voice ID |
|------|----------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` |
| Charlotte | `XB0fDUnXU5powFXDhCwa` |
| Emily | `LcfcDJNUP1GQjkzn1xUU` |

### Voci non più disponibili / rimosse ❌

Adam (`pNInz6obpgDQGcXma3g`), Gigi (`jBpfuIE2acCO8z3wKNM`), Brian (`nPczCjzI2devA6Uv74EC`), Callum (`N2lVS1wCcwneyCShNZwH`), Liam (`TX3LPaxmHKxFHe76RMcY`) e molte altre voci precedentemente standard sono state rimosse dall'API di ElevenLabs e restituiscono errore 404.

💡 **Consiglio**: se vuoi usare una voce specifica, passa a un piano a pagamento di ElevenLabs. Altrimenti **Antoni** è la scelta migliore tra quelle gratis per un podcast.

## Automazione (cron)

Per eseguire automaticamente ogni settimana:

```cron
# Ogni lunedì alle 8:00
0 8 * * 1 cd /home/utente/podcast-generator && .venv/bin/python3 main.py weekly >> cron.log 2>&1
```

## Stack

| Componente | Tecnologia | Costo |
|------------|-----------|-------|
| Scraping | Playwright (Firefox) | Gratuito |
| LLM | Google Gemini 2.5 Flash | Gratuito (250-1000 req/giorno) |
| TTS | ElevenLabs Multilingual v2 | Freemium (10K caratteri/mese gratis) |
| Audio | pydub + FFmpeg | Gratuito |
| CLI | Typer + Rich | Gratuito |
