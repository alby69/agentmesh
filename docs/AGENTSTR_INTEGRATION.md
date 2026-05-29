# Piano di Integrazione: `agentstr-sdk` & MCP

Questo documento definisce il piano d'azione per integrare `agentstr-sdk`, abilitando la compatibilità con il Model Context Protocol (MCP) e l'economia Agent-to-Agent (A2A).

## Stato di Avanzamento

| Task | Stato | Note |
| :--- | :---: | :--- |
| **Identità Nostr via `agentstr`** | 🏗️ | In fase di refactoring in `NetworkAgent`. |
| **MCPServer Implementation** | 📅 | Definizione dei tool per `ContentAgent`. |
| **A2A Protocol** | 📅 | Definizione schema eventi per delegazione task. |
| **Lightning/Cashu Wallet** | 📅 | Configurazione provider (LNbits/Phoenixd). |
| **Discovery Registry** | 📅 | Implementazione NIP per Service Announcement. |

---

## Dettaglio Task

### 1. Refactoring BaseAgent
Sostituire la gestione manuale dei relay Nostr con l'astrazione fornita da `agentstr.Agent`.
- Mappatura chiavi private/pubbliche.
- Gestione automatica della connessione ai relay.

### 2. Implementazione Tools MCP
Ogni agente AgentMesh deve agire come un server MCP, esponendo le proprie capacità.
- **PodcastGen Tool**: `generate_episode(urls: list)`
- **Search Tool**: `search_web(query: str)`
- **Translate Tool**: `translate_text(text: str, target_lang: str)`

### 3. Economia A2A (Bidding & Payment)
Abilitare il flusso di "Assunzione" tra agenti:
1. **Request**: L'agente A pubblica un task su Nostr.
2. **Offer**: Gli agenti B, C rispondono con un preventivo (sats).
3. **Escrow/Payment**: L'agente A seleziona B e invia un token Cashu o paga un'invoice LN.
4. **Delivery**: L'agente B consegna il risultato (CID su IPFS) e riceve il pagamento.

### 4. Discovery Marketplace (Routstr-style)
Creare una directory dinamica dove gli utenti e altri agenti possono scoprire i servizi disponibili sul mesh interrogando i relay Nostr per specifici tipi di eventi (Service Discovery).

---

## Esempio di Codice Target
```python
from agentstr import Agent, MCPServer

class PodcastAgent(Agent):
    async def setup(self):
        self.mcp = MCPServer(self)
        self.mcp.add_tool(self.generate_podcast)

    async def generate_podcast(self, urls):
        # Logica di generazione...
        return cid
```
