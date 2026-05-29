# Roadmap Tecnica PodcastGen 3.0

## 1. Analisi e Stato Avanzamento
PodcastGen 3.0 trasforma un tool monolitico in una flotta di agenti P2P coordinati.

### Milestone Raggiunte (✅)
- **BaseAgent Framework:** Implementata l'interfaccia asincrona per tutti gli agenti.
- **StorageAgent (IPFS):** Integrazione con Pinata e nodi locali per storage immutabile.
- **NetworkAgent (Nostr):** Gestione identità crittografica e pubblicazione NIP-94.
- **SocialAgent (Discovery):** Scansione dei relay Nostr per feed globali.
- **AgentsManager:** Hub centrale per il lifecycle degli agenti nella Web App.

---

## 2. Diagramma di Progetto (Gantt & PERT)

### Cronologia Sviluppo (Gantt)
```mermaid
gantt
    title PodcastGen 3.0 - Roadmap di Sviluppo
    dateFormat  YYYY-MM-DD
    section Fondamenta P2P
    Base Framework & Agents         :done,    des1, 2026-05-25, 2026-05-27
    IPFS & Nostr NIP-94 Core        :done,    des2, 2026-05-27, 2026-05-28
    section Esperienza Utente
    P2P Dashboard & Discovery       :active,  des3, 2026-05-28, 3d
    WebSockets Real-time Updates    :         des4, after des3, 5d
    section Qualità & Sovranità
    Multi-speaker AI (2 voci)       :         des5, 2026-06-05, 7d
    Gestione Chiavi (Seed Phrases)  :         des6, after des4, 4d
    section Produzione
    CI/CD & Docker P2P Config       :         des7, after des6, 3d
```

### Relazioni e Dipendenze (Diagramma PERT)
```mermaid
graph TD
    des1[Fase 1: Base Framework] --> des2[Fase 2: IPFS/Nostr NIP-94]
    des2 --> des3[Fase 3: Dashboard & Discovery]
    des3 --> des4[Fase 4: WebSockets Real-time]
    des4 --> des6[Fase 6: Key Management]
    des5[Fase 5: Multi-speaker AI] --> des7[Fase 7: Production Ready]
    des6 --> des7
    des4 --> des7

    style des1 fill:#dcfce7,stroke:#166534
    style des2 fill:#dcfce7,stroke:#166534
    style des3 fill:#fef9c3,stroke:#854d0e
```

---

## 3. Dettaglio Fasi Future

### Fase 4: Interazione Real-time (WebSockets)
- **Obiettivo:** Notificare l'utente di nuovi podcast scoperti su Nostr in tempo reale.
- **Tasks:** Implementazione `SocialAgent` listener su relay, integrazione FastAPI WebSockets.
- **Stima:** 5 giorni.

### Fase 5: Qualità Audio Avanzata (Multi-speaker)
- **Obiettivo:** Trasformare il monologo in una conversazione tra due host AI.
- **Tasks:** LLM Prompting per script a due voci, orchestrazione TTS con voci multiple (Giuseppe & Elsa).
- **Stima:** 7 giorni.

### Fase 6: Sovranità Totale (Key Management)
- **Obiettivo:** Permettere all'utente di importare la propria chiave Nostr esistente.
- **Tasks:** Pagina Impostazioni per export/import Seed Phrase (NIP-06).
- **Stima:** 4 giorni.

---

## 4. Specifiche Tecniche del Protocollo P2P (Dettaglio)

### Flusso di Pubblicazione (Sequence Diagram)
```mermaid
sequenceDiagram
    participant User
    participant CA as Content Agent
    participant SA as Storage Agent
    participant NA as Network Agent
    participant NR as Nostr Relays

    User->>CA: Richiesta Generazione
    CA->>CA: Fetch & TTS
    CA->>SA: Carica Audio (.mp3)
    SA->>SA: Calcola CID IPFS
    SA-->>CA: Ritorna CID
    CA->>NA: Richiesta Pubblicazione (CID + Metadata)
    NA->>NA: Firma Evento (NIP-94)
    NA->>NR: Broadcast Evento
    NR-->>User: Notifica Nuovo Episodio
```

### Protocolli e NIP Adottati
*   **Identità:** NIP-01 (Basic protocol flow) e NIP-19 (Bech32-encoded keys/events).
*   **Metadata File:** **NIP-94 (File Metadata)**. Questo permette ai client Nostr di riconoscere l'evento come un file multimediale scaricabile.
*   **Discovery:** NIP-02 (Contact List) per seguire altri creatori di podcast.
