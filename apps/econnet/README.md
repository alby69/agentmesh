# EconNet — Simulatore Economico ad Agenti con AI

Simulatore di economia complessa basato su **Modelli ad Agenti (ABM)** e **Apprendimento per Rinforzo (RL)**, integrato nel monorepo [AgentMesh](https://github.com/alby69/agentmesh).

## Motivazione

L'economia classica si fonda sull'ipotesi dell'**Homo Economicus** — un agente perfettamente razionale che massimizza l'utilità conoscendo tutte le informazioni. Nella realtà il comportamento economico è condizionato da emozioni, imitazione sociale, informazione incomplete e fenomeni emergenti che i modelli di equilibrio statico non catturano.

EconNet supera queste limitazioni usando un approccio **bottom-up**: popola il mercato di singoli agenti (consumatori e produttori) che interagiscono in un sistema complesso adattativo, decidendo in base a euristiche psicologiche, reti di influenza sociale e dati storici.

### Concetti chiave

- **Superamento dell'Homo Economicus**: gli agenti non risolvono equazioni di ottimizzazione globale. Hanno uno stato cognitivo (emozioni, budget, suscettibilità sociale) che evolve nel tempo.
- **Prezzo emergente**: il prezzo di mercato non è imposto a priori, ma emerge spontaneamente dalle transazioni bilaterali tra agenti.
- **Rete sociale**: gli agenti sono connessi in un grafo (NetworkX) che simula passaparola ed effetto gregge.
- **AI predittiva**: i produttori usano modelli ML per prevedere la domanda, sperimentando cosa succede quando si tenta di prevedere un sistema riflessivo.
- **Visualizzazione**: andamento dei prezzi, bolle speculative e crash in tempo reale con matplotlib.

## Quick Start

```bash
# Installa
uv sync --package econnet

# Esegui una simulazione base
uv run python -m econnet --ticks 500 --consumers 100 --producers 10

# Con visualizzazione
uv run python -m econnet --ticks 500 --visualize
```

## Struttura

```
apps/econnet/
├── main.py                          # CLI entry point
├── pyproject.toml                   # Dipendenze
├── README.md
├── ROADMAP.md                       # Piano di implementazione
├── econnet/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── consumer.py              # ConsumerAgent (budget, emozioni, euristiche)
│   │   ├── producer.py              # ProducerAgent (pricing dinamico, scorte, ML)
│   │   └── base.py                  # BaseAgent con stato comune
│   ├── network/
│   │   ├── __init__.py
│   │   └── social_graph.py          # Grafo di influenza sociale (NetworkX)
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── engine.py                # Motore tick-by-tick
│   │   ├── market.py                # Mercato (ordine book, transazioni)
│   │   └── events.py                # Eventi e cronologia
│   └── visualization/
│       ├── __init__.py
│       └── plots.py                 # Grafici matplotlib (prezzi, bolle, crash)
└── tests/
    ├── __init__.py
    └── test_simulation.py           # Test del motore di simulazione
```

## Architettura

### ConsumerAgent

Ogni consumatore ha:
- **Budget**: risorse monetarie disponibili
- **Stato emotivo**: vettore [soddisfazione, paura, entusiasmo, imitazione]
- **Soglia di acquisto**: decidesse quando comprare in base a prezzo percepito vs utilità
- **Rete sociale**: liste di vicini che influenzano le decisioni

### ProducerAgent

Ogni produttore ha:
- **Scorte**: unità di prodotto disponibili
- **Prezzo attuale**: aggiornato dinamicamente
- **Modello predittivo**: rete neurale semplice che stima la domanda futura
- **Strategia**: pricing basato su costi, domanda prevista e concorrenza

### Market

Il mercato è un order book decentralizzato:
- Gli agenti pubblicano offerte/domande
- Le transazioni avvengono bilateralmente
- Il prezzo emerge dall'incontro domanda-offerta
- Nessun prezzo di equilibrio imposto

### Social Graph

Grafo NetworkX dove:
- I nodi sono agenti (consumatori e produttori)
- Gli archi rappresentano influenza sociale
- L'effetto gregge si manifesta come cascata di decisioni simili
- La rete evolve nel tempo (archi si creano/rompono)

## Stack

- **Python 3.10+**, async/simulazione sincrona
- **NetworkX**: grafi e reti sociali
- **NumPy / Pandas**: dati e calcoli
- **Matplotlib**: visualizzazione
- **PyTorch** (opzionale): reti neurali per agenti produttori
- **pytest**: testing
