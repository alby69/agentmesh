# Piano di Integrazione: `agentstr-sdk`, MCP & Marketplace

Questo documento descrive la strategia per integrare `agentstr-sdk` per abilitare la compatibilità MCP, i micropagamenti e l'economia Agent-to-Agent (A2A).

## Obiettivi Core
1.  **Compatibilità MCP**: Agenti capaci di usare tool esterni standardizzati.
2.  **Economia A2A**: Delegazione di task tra agenti con pagamenti automatici (Lightning/Cashu).
3.  **Discovery & Bidding**: Un marketplace permissionless ispirato a **Routstr**.

---

## Fase 1: Refactoring con `agentstr`
- Integrare `agentstr.Agent` per la gestione dell'identità e dei messaggi.
- Abilitare il supporto nativo per i wallet Lightning/Cashu.

## Fase 2: Agent-to-Agent (A2A) Economy
Implementare il pattern di delegazione economica:
- **Esempio**:
    1. `ContentAgent` ha bisogno di una traduzione.
    2. Cerca un `TranslationAgent` via Nostr (Discovery Layer).
    3. Il `TranslationAgent` risponde con un prezzo (es. 10 sats).
    4. `ContentAgent` paga l'invoice via Lightning e riceve il risultato.

## Fase 3: Marketplace & Bidding (Routstr Style)
- **Annunci di Servizio**: Gli agenti pubblicano eventi Nostr con metadati su skills, latenza e prezzo.
- **Smart Bidding**: Gli agenti possono richiedere preventivi a più provider e selezionare il migliore in base alla reputazione (Web of Trust).

## Fase 4: Integrazione MCP
- Ogni agente espone un `MCPServer`.
- Esempio: PodcastGen espone il tool `generate_audio` che altri agenti nel mesh possono chiamare a pagamento.

---

## Prossimi Passi Tecnici
1. Prototipo di workflow A2A in `packages/agentmesh-core/examples/`.
2. Implementazione del sistema di reputazione basato su feedback (eventi Nostr post-task).
