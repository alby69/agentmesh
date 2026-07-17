# EconNet — Simulatore Economico ad Agenti con AI

Simulatore di economia complessa basato su **Modelli ad Agenti (ABM)** e **Apprendimento per Rinforzo (RL)**, integrato nel monorepo [AgentMesh](https://github.com/alby69/agentmesh).

## Motivazione

L'economia classica si fonda sull'ipotesi dell'**Homo Economicus** — un agente perfettamente razionale che massimizza l'utilità conoscendo tutte le informazioni. Nella realtà il comportamento economico è condizionato da emozioni, imitazione sociale, informazione incomplete e fenomeni emergenti che i modelli di equilibrio statico non cauturano.

EconNet supera queste limitazioni usando un approccio **bottom-up**: popola il mercato di singoli agenti (consumatori e produttori) che interagiscono in un sistema complesso adattativo, decidendo in base a euristiche psicologiche, reti di influenza sociale e dati storici.

### Concetti chiave

- **Superamento dell'Homo Economicus**: gli agenti non risolvono equazioni di ottimizzazione globale. Hanno uno stato cognitivo (emozioni, budget, suscettibilità sociale) che evolve nel tempo.
- **Prezzo emergente**: il prezzo di mercato non è imposto a priori, ma emerge spontaneamente dalle transazioni bilaterali tra agenti (limit orders).
- **Rete sociale**: gli agenti sono connessi in un grafo (NetworkX) che simula passaparola ed effetto gregge, influenzando la soddisfazione e le propensioni all'acquisto.
- **AI predittiva (Producers)**: i produttori utilizzano una rete neurale artificiale in PyTorch (`DemandForecaster`) per prevedere la domanda futura online tramite discesa stocastica del gradiente (SGD) tick-by-tick.
- **Reinforcement Learning (Consumers)**: i consumatori utilizzano algoritmi di Q-learning per apprendere strategie d'acquisto adattative in base a prezzo, budget e sentiment.
- **Scenari Macroeconomici**: simulatore di scenari storici e complessi (Bolla 2008, Crisi pandemia, Boom tecnologico) con rilevamento analitico di bolle speculative, crash di mercato, stagflazione e trend laterali.
- **Visualizzazioni e Web Dashboard**: interfaccia grafica integrata in FastAPI + HTMX per lanciare scenari, avanzare step-by-step ed esplorare grafici della struttura sociale e dei trend di mercato in tempo reale.

## Quick Start

```bash
# Installa le dipendenze del workspace
uv sync --all-packages --all-extras

# Avvia l'interfaccia grafica Web interattiva (FastAPI + HTMX)
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --server --port 8080

# Esegui una simulazione di confronto tra comportamento euristico e ABM + AI
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --compare --ticks 150

# Esegui uno scenario predefinito (Bolla 2008) via CLI
PYTHONPATH=apps/econnet uv run python apps/econnet/main.py --scenario bolla-2008 --ticks 200 --visualize
```

## Struttura

```
apps/econnet/
├── main.py                          # CLI entry point e web server hook
├── pyproject.toml                   # Dipendenze (NetworkX, PyTorch, FastAPI, etc.)
├── README.md
├── ROADMAP.md                       # Piano di implementazione (100% Completato)
├── econnet/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── consumer.py              # ConsumerAgent (budget, emozioni, Q-Learning RL)
│   │   ├── producer.py              # ProducerAgent (pricing dinamico, scorte, PyTorch demand forecast)
│   │   ├── ml_models.py             # DemandForecaster PyTorch MLP
│   │   └── base.py                  # BaseAgent con stato comune
│   ├── network/
│   │   ├── __init__.py
│   │   └── social_graph.py          # Grafo di influenza sociale e propagazione
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── engine.py                # Motore tick-by-tick e detector anomalie
│   │   ├── market.py                # Mercato (limit order book bilaterale)
│   │   ├── scenarios.py             # Scenario manager & comparatore modelli
│   │   └── events.py                # Event Bus strutturato (Crash, Transaction, PriceChange)
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py                 # Rendering matplotlib (prezzi, Gini, rete sociale)
│   └── web/
│       ├── __init__.py
│       └── app.py                   # FastAPI + HTMX Dashboard interattiva
└── tests/
    ├── __init__.py
    ├── test_new_features.py         # Test delle nuove funzionalità (RL, ML, Web, Scenarios)
    └── test_simulation.py           # Test base della simulazione
```

## Architettura

### ConsumerAgent

Ogni consumatore ha:
- **Budget**: risorse monetarie disponibili.
- **Stato emotivo**: vettore `[soddisfazione, paura, entusiasmo, imitazione]`.
- **Decisore Ibrido**: a scelta tra euristica cognitiva classica o agente di apprendimento per rinforzo con **Q-learning** discreto basato sull'ottimizzazione del proprio reward (soddisfazione e conservazione del capitale).

### ProducerAgent

Ogni produttore ha:
- **Scorte e Produzione**: gestione magazzino basata su tassi di produzione e costi unitari.
- **Demand Forecasting**: stima dinamica tramite rete neurale multistrato (MLP) in PyTorch addestrata online step-by-step con algoritmo SGD.

### Market

Il mercato gestisce un order book bilaterale trasparente:
- Incrocia ordini limitati ordinando le domande dal prezzo massimo e le offerte dal prezzo minimo.
- Calcola il prezzo di equilibrio emergente e regola lo scambio monetario.

### Social Graph

Un grafo dinamico (Watts-Strogatz o Barabasi-Albert):
- Consente la propagazione del sentiment/informazione tra nodi.
- Misura l'effetto gregge ed evolve la topologia eliminando o creando connessioni casuali ad ogni tick.

## Testing

Per eseguire la suite di test completa (17 test unitari e di integrazione passati con successo):

```bash
uv run pytest apps/econnet
```
