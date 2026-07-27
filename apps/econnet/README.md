# EconNet — Simulatore Economico ad Agenti con AI

Simulatore di economia complessa basato su **Modelli ad Agenti (ABM)** e **Apprendimento per Rinforzo (RL)**, integrato nel monorepo [AgentMesh](https://github.com/alby69/agentmesh).

## Motivazione

L'economia classica si fonda sull'ipotesi dell'**Homo Economicus** — un agente perfettamente razionale che massimizza l'utilità conoscendo tutte le informazioni. Nella realtà il comportamento economico è condizionato da emozioni, imitazione sociale, informazione incomplete e fenomeni emergenti che i modelli di equilibrio statico non catturano.

EconNet supera queste limitazioni usando un approccio **bottom-up**: popola il mercato di singoli agenti (consumatori e produttori) che interagiscono in un sistema complesso adattativo, decidendo in base a euristiche psicologiche, reti di influenza sociale e dati storici.

### Concetti chiave

- **Superamento dell'Homo Economicus**: gli agenti non risolvono equazioni di ottimizzazione globale. Hanno uno stato cognitivo (emozioni, budget, suscettibilità sociale) che evolve nel tempo.
- **Prezzo emergente**: il prezzo di mercato non è imposto a priori, ma emerge spontaneamente dalle transazioni bilaterali tra agenti.
- **Rete sociale**: gli agenti sono connessi in un grafo (NetworkX) che simula passaparola ed effetto gregge.
- **AI predittiva (DemandForecaster)**: i produttori usano reti neurali PyTorch ad aggiornamento continuo online per prevedere la domanda aggregata.
- **Apprendimento per Rinforzo (QLearner)**: i consumatori usano algoritmi discreti di Q-learning per ottimizzare dinamicamente le loro decisioni di acquisto tick dopo tick.
- **Pace Sociale & Credito (Graeberian Mode)**: simula sistemi di fiducia basati sull'estensione del credito virtuale, tributi reciproci e fallimenti (default) coordinati da un parametro di coesione sociale.
- **Dashboard Interattiva**: pannello web completo FastAPI + HTMX + Plotly per controllare e analizzare la simulazione visivamente.

## Quick Start

### Esecuzione CLI standard

```bash
# Esegui una simulazione base
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --ticks 200

# Con grafici statici matplotlib (prezzi, emozioni, budget, crash)
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --ticks 500 --visualize

# Più agenti, rete scale-free
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --ticks 300 --consumers 200 --producers 20 --network scale-free --visualize
```

### Avvio Dashboard Interattiva Web (FastAPI + HTMX)

```bash
# Lancia il server web interattivo su http://localhost:8000
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --server --port 8000
```

Con la Dashboard Web puoi:
- Scegliere scenari preimpostati (es. "Bolla 2008", "Crisi pandemia", "Boom tecnologico").
- Avanzare di 1, 10 o 50 Tick alla volta.
- Visualizzare in tempo reale i grafici interattivi di Plotly (prezzi, indice Gini di disuguaglianza, effetto gregge).
- Reset istantaneo e monitoraggio delle metriche di rete NetworkX.

### Output

- **Console**: riepilogo alla fine (prezzo, volatilità, transazioni, densità rete, metriche Graeber)
- **`--visualize`**: genera 5 grafici PNG nella cartella di output (`econnet_sim_price.png`, `_emotions.png`, `_budgets.png`, `_crashes.png`, `_graeber.png`)
- **`--output log.json`**: salva il log di ogni tick in JSON per analisi successiva
- **`--output-dir path/`**: cartella dove salvare i file (default: `apps/econnet/output/`)

## Struttura

```
apps/econnet/
├── main.py                          # CLI entry point e Web Launcher
├── pyproject.toml                   # Dipendenze
├── README.md
├── ROADMAP.md                       # Piano di implementazione completo (Fase 1-5 completate!)
├── econnet/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── consumer.py              # ConsumerAgent (budget, emozioni, euristiche, QLearner RL)
│   │   ├── producer.py              # ProducerAgent (pricing dinamico, scorte, PyTorch DemandForecaster)
│   │   └── base.py                  # BaseAgent con stato comune
│   ├── network/
│   │   ├── __init__.py
│   │   └── social_graph.py          # Grafo sociale (NetworkX, herd effect, sentiment propagation)
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── engine.py                # Motore tick-by-tick (Eventi di classe, indice Gini)
│   │   ├── market.py                # Mercato (ordine book, transazioni)
│   │   ├── scenarios.py             # ScenarioManager con presets ("Bolla 2008", etc.)
│   │   └── events.py                # Eventi di classe e EventBus
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py                 # Grafici matplotlib (prezzi, bolle, crash)
│   └── web/
│       ├── __init__.py
│       └── app.py                   # Dashboard Web FastAPI + HTMX + Plotly
└── tests/
    ├── __init__.py
    ├── test_graeber.py
    ├── test_ml.py                   # Test unitari QLearner e DemandForecaster
    ├── test_scenarios.py            # Test ScenarioManager ed eventi
    └── test_simulation.py           # Test motore e mercato
```

## Architettura

### ConsumerAgent

Ogni consumatore ha:
- **Budget & Classe Sociale**: risorse monetarie disponibili che definiscono lo stato sociale (low, medium, high).
- **Stato emotivo**: vettore [soddisfazione, paura, entusiasmo, imitazione].
- **Q-Learning**: discretizza lo stato economico/sociale e impara la politica d'acquisto ottimale per massimizzare la soddisfazione a lungo termine e minimizzare il debito.

### ProducerAgent

Ogni produttore ha:
- **Scorte & Produzione**: unità prodotte per tick entro i costi di budget.
- **PyTorch SGD Demand Forecaster**: rete neurale a 3 input (prezzo, volume, sentimento) che stima la domanda del tick successivo con aggiornamento online.
- **Pricing dinamico**: varia il prezzo in base a scorte disponibili, forecast ML, e concorrenza.

### Market

Il mercato è un order book decentralizzato:
- Gli agenti pubblicano offerte/domande.
- Le transazioni avvengono bilateralmente.
- Il prezzo emerge dall'incontro domanda-offerta.
- Supporta transazioni basate su credito virtuale.

### Social Graph

Grafo NetworkX dove:
- I nodi sono agenti (consumatori e produttori).
- Gli archi rappresentano influenza sociale.
- Calcola in tempo reale metriche complesse como **Herd Effect** (effetto gregge) e **Sentiment Propagation** (propagazione del sentiment dei vicini).

## Stack

- **Python 3.10+**
- **NetworkX**: grafi e reti sociali
- **NumPy / Pandas**: dati e calcoli
- **Matplotlib / Plotly**: visualizzazione statica e interattiva
- **PyTorch**: reti neurali predittive online
- **FastAPI / Uvicorn / HTMX**: server e dashboard web interattiva
- **pytest**: testing automatico
