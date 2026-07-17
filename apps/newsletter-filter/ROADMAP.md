# ROADMAP: Newsletter Filter & Extraction App / Agent (v4.0.1)

Questo documento presenta la pianificazione delle fasi per l'applicazione **Newsletter Filter & Extraction** (`apps/newsletter-filter/`).

---

## Stato dell'Arte ed Evoluzione in Tre Fasi

```
┌───────────────────────────────────────────────────────────┐
│ FASE 1: Core Filtering Agent & Extraction Engine          │ <--- [COMPLETATO]
│ - Sviluppo di apps/newsletter-filter come workspace member│
│ - Definizione del FilterAgent (disaccoppiato)              │
│ - Integrazione con l'infrastruttura di scraping ed IMAP   │
│ - Implementazione dei prompt cognitivi con agentmesh-llm  │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ FASE 2: Integrazione UI & Workflow (The App UI)           │ <--- [COMPLETATO]
│ - Web UI interattiva (FastAPI + HTMX) in apps/             │
│ - Pannello per configurare sorgenti, keyword e query      │
│ - Pipeline di comunicazione asincrona tra le due app      │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ FASE 3: Mesh Automation & A2A Economy                    │ <--- [PIANIFICATO / IN CORSO]
│ - Registrazione del FilterAgent sulla rete Nostr          │
│ - Schedulazione automatica delle query via APScheduler    │
│ - Abilitazione di micropagamenti Lightning/Cashu per query│
└───────────────────────────────────────────────────────────┘
```

---

## Dettaglio delle Fasi

### FASE 1: Core Filtering Agent & Extraction Engine [COMPLETATO]
La prima fase si è concentrata sulla creazione del modulo applicativo asincrono `apps/newsletter-filter` completamente autonomo e disaccoppiato.
- **`pyproject.toml`** configurato correttamente come workspace member del monorepo.
- **`FilterAgent`** implementato, ereditando da `BaseAgent` e comunicando tramite il protocollo standard `AgentMessage`.
- Modulo **`fetcher.py`** in grado di recuperare articoli da RSS e tramite protocollo IMAP con `imap-tools` e `trafilatura`.
- Modulo **`engine.py`** per l'orchestrazione del recupero e filtraggio cognitivo con `agentmesh-llm` per analizzare, valutare e sintetizzare gli articoli in formato JSON.
- Test automatici scritti e passanti con successo.

---

### FASE 2: Integrazione UI & Workflow (The App UI) [COMPLETATO]
Questa fase introduce l'interfaccia utente web e l'integrazione asincrona tra le applicazioni.
- **Web UI Interattiva**: Creazione di un'app FastAPI con HTMX per visualizzare le newsletter analizzate, con filtri per punteggio di rilevanza, rilevanza semantica e pulsanti per l'avvio asincrono del filtraggio.
- **Persistenza (Database SQL/SQLite)**: Memorizzazione delle impostazioni dell'utente (provider, modello, cartella IMAP, query predefinita, URL RSS) e di tutti gli articoli analizzati.
- **Pipeline asincrona tra le app**: Implementazione di un pulsante per l'invio asincrono degli articoli filtrati più rilevanti direttamente a `podcast-generator` tramite API REST per la generazione automatica di un episodio podcast.

---

### FASE 3: Mesh Automation & A2A Economy [PIANIFICATO]
- **Integrazione Nostr**: Abilitazione della comunicazione asincrona tra `FilterAgent` e altri agenti tramite la rete Nostr (Kind 29001).
- **Automazione via APScheduler**: Schedulazione periodica del fetch e del filtraggio automatico delle email e dei feed RSS (es. ogni mattina alle 8:00) per trovare i contenuti rilevanti senza intervento umano.
- **A2A Economy**: Abilitazione di micropagamenti (Lightning/Cashu) per l'interrogazione e il recupero dei contenuti filtrati da altri agenti.
