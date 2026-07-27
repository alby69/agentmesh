# ROADMAP — EconNet Simulatore Economico ad Agenti

Piano di implementazione in fasi per il simulatore di economia complessa basato su ABM + AI.

---

## Fase 1: Struttura Base e Agenti ✅ COMPLETATA

Definizione delle fondamenta del simulatore: package, classi base, configurazione.

### 1.1 Package setup ✅
- [x] `pyproject.toml` con dipendenze (networkx, numpy, pandas, matplotlib)
- [x] Struttura moduli: `agents/`, `network/`, `simulation/`, `visualization/`
- [x] Entry point CLI `main.py`
- [x] Test suite `tests/`

### 1.2 BaseAgent ✅
- [x] Classe astratta con stato comune (id, tipo, budget)
- [x] Interfaccia `step()` per ogni tick di simulazione
- [x] Serializzazione stato per logging

### 1.3 ConsumerAgent ✅
- [x] Stato emotivo: vettore [soddisfazione, paura, entusiasmo, imitazione]
- [x] Budget dinamico (guadagna consumando, spende acquistando)
- [x] Soglia di acquisto basata su prezzo percepito vs utilità
- [x] Euristiche: avversione alla perdita, ancoraggio, effetto gregge
- [x] Reazione a prezzi e pubblicità

### 1.4 ProducerAgent ✅
- [x] Gestione scorte e produzione
- [x] Pricing dinamico (cost-plus, domanda, concorrenza)
- [x] Modello predittivo base (media mobile esponenziale)
- [x] Budget e profitti

### 1.5 Configurazione ✅
- [x] Parametri simulazione (tick, agenti, tassi)
- [x] Parametri di default ragionevoli
- [x] Override via CLI o dizionario

---

## Fase 2: Rete Sociale e Mercato ✅ COMPLETATA

Implementazione della topologia di rete e del meccanismo di mercato.

### 2.1 Social Graph ✅
- [x] Grafo NetworkX con agenti como nodi
- [x] Archi pesati per forza di influenza
- [x] Generazione topologie: random, small-world, scale-free
- [x] Evoluzione dinamica della rete (creazione/rottura archi)
- [x] Misura diffusione informazione e effetto gregge

### 2.2 Market (Order Book) ✅
- [x] Order book decentralizzato
- [x] Ordini di acquisto/vendita con prezzo desiderato
- [x] Matching bilaterale domanda-offerta
- [x] Prezzo emergente (nessun equilibrio imposto)
- [x] Storico transazioni per ogni tick

### 2.3 Event System ✅
- [x] Classi evento: `PriceChange`, `Transaction`, `AgentDecision`, `MarketCrash`
- [x] Event bus per logging e callback
- [x] Registro eventi per analisi post-simulazione

---

## Fase 3: Motore di Simulazione ✅ COMPLETATA

Il cuore del sistema: orchestrare agenti, mercato e rete tick dopo tick.

### 3.1 SimulationEngine ✅
- [x] Loop tick-by-tick con conteggio tempo
- [x] Ordine di esecuzione: producer → market → consumer → network
- [x] Pause/resume simulazione
- [x] Seed randomico per riproducibilità
- [x] Logging strutturato per ogni tick

### 3.2 Ciclo di Simulazione ✅
- [x] **Tick N**:
  1. Ogni Producer aggiorna scorte e prezzo (pricing dinamico)
  2. Il Market processa ordini in sospeso
  3. Ogni Consumer valuta acquisto (stato emotivo + prezzo + rete)
  4. Le transazioni avvengono e aggiornano budget
  5. La Social Graph propaga influenza
  6. I modelli predittivi dei Producer si aggiornano con nuovi dati

### 3.3 Fenomeni Emergenti ✅
- [x] Bolle speculative (prezzo sale senza fondamento)
- [x] Crash improvvisi (cascata di vendite)
- [x] Effetto gregge (acquisti simultanei)
- [x] Stagflazione (prezzo alto + bassa domanda)
- [x] Mercati laterali (stabilità temporanea)

---

## Fase 4: AI e Machine Learning ✅ COMPLETATA

Integrazione dei modelli di apprendimento negli agenti.

### 4.1 Modello Predittivo Produttore ✅
- [x] Rete neurale semplice (PyTorch) per forecasting domanda
- [x] Input: storico prezzi, volume transazioni, stato emotivo medio
- [x] Output: domanda prevista per prossimo tick
- [x] Training online (aggiornamento continuo dopo ogni tick)

### 4.2 Reinforcement Learning Consumatore ✅
- [x] Stato: [prezzo, budget, soddisfazione, pressione sociale]
- [x] Azioni: acquista / non acquista / compra di più
- [x] Ricompensa: soddisfazione post-acquisto
- [x] Algoritmo: Q-learning semplice o policy gradient

### 4.3 Riflessività ✅
- [x] Quando il modello predittivo cambia, i produttori cambiano prezzo
- [x] Il cambio prezzo modifica il comportamento dei consumatori
- [x] Il cambiamento dei consumatori invalida la previsione
- [x] Ciclo continuo: testare cosa succede quando la previsione crea la realtà

### 4.4 Confronto Modelli ✅
- [x] Eseguire simulazione con agenti puramente razionali
- [x] Eseguire simulazione con agenti ABM+AI
- [x] Confrontare: crash predetti, stabilità, distribuzione ricchezza
- [x] Report differenze

---

## Fase 5: Visualizzazione e Analisi ✅ COMPLETATA

Visualizzare i risultati e analizzare i fenomeni emergenti.

### 5.1 Dashboard Grafici ✅
- [x] Andamento prezzo nel tempo (line chart)
- [x] Volume transazioni per tick (bar chart)
- [x] Distribuzione budget agenti (istogramma)
- [x] Stato emotivo medio consumatori (line chart multi-asse)
- [x] Rete sociale con colori per stato (grafo)

### 5.2 Indicatori ✅
- [x] Indice di volatilità
- [x] Indice di disuguaglianza (Gini coefficient)
- [x] Indice di efficienza del mercato
- [x] Indice di coesione sociale

### 5.3 Scenario Manager ✅
- [x] Configurare scenari predefiniti: "Bolla 2008", "Crisi pandemia", "Boom tecnologico"
- [x] Confronto parallelo scenari
- [x] Export risultati in CSV/JSON

### 5.4 Web UI ✅
- [x] Dashboard FastAPI + HTMX per lanciare simulazioni
- [x] Grafici interattivi con Plotly
- [x] Stato simulazione in tempo reale

---

## Note Architetturali

### Principio: Bottom-Up, non Top-Down

L'economia classica parte dai modelli (teoria → equazioni → dati).
EconNet parte dai dati e dai comportamenti (agenti → interazioni → emergenza).

### Paradigma: Complessità Adattativa

Il mercato è un **sistema complesso adattativo** (CAS):
- Molti agenti autonomi
- Interazioni locali (non globali)
- Comportamento che si adatta
- Fenomeni emergenti imprevedibili

### Riflessività

Quando un modello predittivo viene reso pubblico e usato dagli agenti, il sistema cambia. EconNet simula questo ciclo per mostrare che le previsioni economiche sono per natura auto-contraddittorie.

### Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| Agenti | Python classi + euristiche + Q-learning |
| Rete sociale | NetworkX (graph) |
| Mercato | Order book custom |
| ML | PyTorch (rette neurali) o scikit-learn |
| Dati | NumPy, Pandas |
| Visualizzazione | Matplotlib (+ Plotly per web) |
| Test | pytest, pytest-asyncio |
| Build | hatchling, uv workspace |

---

## Fase 6: Monorepo Integration & Standardization ✅ COMPLETATA

Allineamento al template standard del monorepo e integrazione con i pacchetti core.

- [x] **Refactor `BaseEconAgent`**: eredita da `agentmesh_core.BaseAgent`
- [x] **Configurazione con `pydantic-settings`**: aggiunto `config.py` per caricare parametri tramite variabili d'ambiente (`ECONNET_`)
- [x] **Dipendenze monorepo**: aggiunto `agentmesh-core` e `agentmesh-relay` come dipendenze UV workspace in `pyproject.toml`

## Fase 7: Persistence & REST API ✅ COMPLETATA

Persistenza delle simulazioni in formato SQLite con WAL mode.

- [x] **SQLite WAL Schema**: implementato in `web/db.py` con tabelle per `simulations`, `ticks`, `agents`, `transactions`, `events`
- [x] **Integrazione con `main.py`**: salvataggio automatico se eseguito con flag `--output-db`
- [x] **Integrazione con Dashboard**: tabella di visualizzazione ed eliminazione delle simulazioni passate direttamente nel browser

## Fase 8: Advanced AI & Multi-Agent Economy ✅ COMPLETATA

Evoluzione della complessità economica e del livello di intelligenza degli agenti.

- [x] **DQN (Deep Q-Network)**: implementato in `agents/dqn_consumer.py` usando PyTorch continuo, con replay buffer e target network per `ConsumerAgent`
- [x] **Multi-Good Market**: aggiunta la classe `Product` in `simulation/product.py` e supporto per molteplici order-book separati in `Market`
- [x] **Pricing e Decisioni Multi-Bene**: i produttori e consumatori supportano tracciamento e decisioni separate per bene

## Fase 9: Decentralized Simulation Mesh ✅ COMPLETATA

Connessione di EconNet alla mesh decentralizzata P2P di AgentMesh.

- [x] **Nostr Event Stream**: implementato `relay/publisher.py` con `EconNetNostrPublisher` per pubblicare aggiornamenti sui prezzi, transazioni e crash di mercato su Nostr
- [x] **Standardizzazione dei Messaggi**: eventi firmati e pubblicati come NIP-01 text notes con tag custom (`econnet-price`, `econnet-tx`, `econnet-crash`)

## Fase 10: Advanced UX & Analytics ✅ COMPLETATA

- [x] **Price Charts per Product**: grafici interattivi multi-asse di Plotly che mostrano l'evoluzione dei prezzi per singolo prodotto della simulazione
- [x] **Simulation Manager in UI**: interfaccia per salvare, elencare e pulire le simulazioni passate memorizzate in SQLite
