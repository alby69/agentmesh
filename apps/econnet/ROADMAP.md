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

## Fase 2: Rete Sociale e Mercato ⬜ IN CORSO

Implementazione della topologia di rete e del meccanismo di mercato.

### 2.1 Social Graph ⬜
- [ ] Grafo NetworkX con agenti come nodi
- [ ] Archi pesati per forza di influenza
- [ ] Generazione topologie: random, small-world, scale-free
- [ ] Evoluzione dinamica della rete (creazione/rottura archi)
- [ ] Misura diffusione informazione e effetto gregge

### 2.2 Market (Order Book) ⬜
- [ ] Order book decentralizzato
- [ ] Ordini di acquisto/vendita con prezzo desiderato
- [ ] Matching bilaterale domanda-offerta
- [ ] Prezzo emergente (nessun equilibrio imposto)
- [ ] Storico transazioni per ogni tick

### 2.3 Event System ⬜
- [ ] Classi evento: `PriceChange`, `Transaction`, `AgentDecision`, `MarketCrash`
- [ ] Event bus per logging e callback
- [ ] Registro eventi per analisi post-simulazione

---

## Fase 3: Motore di Simulazione ⬜

Il cuore del sistema: orchestrare agenti, mercato e rete tick dopo tick.

### 3.1 SimulationEngine ⬜
- [ ] Loop tick-by-tick con conteggio tempo
- [ ] Ordine di esecuzione: producer → market → consumer → network
- [ ] Pause/resume simulazione
- [ ] Seed randomico per riproducibilità
- [ ] Logging strutturato per ogni tick

### 3.2 Ciclo di Simulazione ⬜
- [ ] **Tick N**:
  1. Ogni Producer aggiorna scorte e prezzo (pricing dinamico)
  2. Il Market processa ordini in sospeso
  3. Ogni Consumer valuta acquisto (stato emotivo + prezzo + rete)
  4. Le transazioni avvengono e aggiornano budget
  5. La Social Graph propaga influenza
  6. I modelli predittivi dei Producer si aggiornano con nuovi dati

### 3.3 Fenomeni Emergenti ⬜
- [ ] Bolle speculative (prezzo sale senza fondamento)
- [ ] Crash improvvisi (cascata di vendite)
- [ ] Effetto gregge (acquisti simultanei)
- [ ] Stagflazione (prezzo alto + bassa domanda)
- [ ] Mercati laterali (stabilità temporanea)

---

## Fase 4: AI e Machine Learning ⬜

Integrazione dei modelli di apprendimento negli agenti.

### 4.1 Modello Predittivo Produttore ⬜
- [ ] Rete neurale semplice (PyTorch) per forecasting domanda
- [ ] Input: storico prezzi, volume transazioni, stato emotivo medio
- [ ] Output: domanda prevista per prossimo tick
- [ ] Training online (aggiornamento continua dopo ogni tick)

### 4.2 Reinforcement Learning Consumatore ⬜
- [ ] Stato: [prezzo, budget, soddisfazione, pressione sociale]
- [ ] Azioni: acquista / non acquista / compra di più
- [ ] Ricompensa: soddisfazione post-acquisto
- [ ] Algoritmo: Q-learning semplice o policy gradient

### 4.3 Riflessività ⬜
- [ ] Quando il modello predittivo cambia, i produttori cambiano prezzo
- [ ] Il cambio prezzo modifica il comportamento dei consumatori
- [ ] Il cambiamento dei consumatori invalida la previsione
- [ ] Ciclo continuo: testare cosa succede quando la previsione crea la realtà

### 4.4 Confronto Modelli ⬜
- [ ] Eseguire simulazione con agenti puramente razionali
- [ ] Eseguire simulazione con agenti ABM+AI
- [ ] Confrontare: crash predetti, stabilità, distribuzione ricchezza
- [ ] Report differenze

---

## Fase 5: Visualizzazione e Analisi ⬜

Visualizzare i risultati e analizzare i fenomeni emergenti.

### 5.1 Dashboard Grafici ⬜
- [ ] Andamento prezzo nel tempo (line chart)
- [ ] Volume transazioni per tick (bar chart)
- [ ] Distribuzione budget agenti (istogramma)
- [ ] Stato emotivo medio consumatori (line chart multi-asse)
- [ ] Rete sociale con colori per stato (grafo)

### 5.2 Indicatori ⬜
- [ ] Indice di volatilità
- [ ] Indice di disuguaglianza (Gini coefficient)
- [ ] Indice di efficienza del mercato
- [ ] Indice di coesione sociale

### 5.3 Scenario Manager ⬜
- [ ] Configurare scenari predefiniti: "Bolla 2008", "Crisi pandemia", "Boom tecnologico"
- [ ] Confronto parallelo scenari
- [ ] Export risultati in CSV/JSON

### 5.4 Web UI (opzionale) ⬜
- [ ] Dashboard FastAPI + HTMX per lanciare simulazioni
- [ ] Grafici interattivi con Plotly
- [ ] Stato simulazione in tempo reale

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
| Agenti | Python classi + euristiche |
| Rete sociale | NetworkX (graph) |
| Mercato | Order book custom |
| ML | PyTorch (rette neurali) o scikit-learn |
| Dati | NumPy, Pandas |
| Visualizzazione | Matplotlib (+ Plotly per web) |
| Test | pytest, pytest-asyncio |
| Build | hatchling, uv workspace |
