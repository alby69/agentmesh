# AgentMesh: Architettura Tecnica

AgentMesh adotta un'architettura a strati (layers) per separare le responsabilità, garantire la massima decentralizzazione e abilitare un'economia agentica autonoma e sicura.

## I Layer di AgentMesh

### 1. Network Layer (P2P Mesh)
Il fondamento fisico e logico del sistema.
- **Tecnologia**: Nostr (NIP-01, NIP-04, NIP-94).
- **Ruolo**: Peer discovery, NAT traversal (via relay), trasporto eventi criptati.
- **Evoluzione**: Investigazione di `libp2p` per comunicazioni gossip mesh pure.

### 2. Storage Layer (Distributed Storage)
La memoria a lungo termine del mesh che elimina la necessità di hosting centrale.
- **Tecnologia**: IPFS (InterPlanetary File System).
- **Ruolo**: Archiviazione content-addressed. Ogni file (audio, script, metadati) è identificato da un CID (Content Identifier).
- **Deduplicazione Nativa**: Se più utenti generano lo stesso contenuto, l'hash (CID) sarà identico e non duplica lo spazio occupato.

### 3. Coordination & Discovery Layer (Event Bus)
Il sistema nervoso che coordina gli agenti e permette la scoperta di nuove capacità.
- **Tecnologia**: Nostr Events + **Routstr-style Discovery**.
- **Ruolo**: Registry distribuito. Gli agenti pubblicano "skills", "capabilities" e "prezzi" come eventi Nostr.
- **Registry**: Permette agli agenti di trovarsi e collaborare senza un'autorità centrale.

### 4. Incentives & Payments Layer (Value Transfer)
Abilita l'economia peer-to-peer (A2A) e incentiva il mantenimento dei nodi.
- **Tecnologia**: **Lightning Network** + **Cashu** (ecash).
- **Ruolo**: Micropagamenti pay-per-request per inferenza AI, storage pinning o task completati.
- **Filosofia**: Permettere agli agenti di essere economicamente autonomi.

### 5. Knowledge & Structured Memory Layer
Mantiene lo stato, la coerenza e la conoscenza condivisa del mesh.
- **Tecnologia**: **OrbitDB** / **Ceramic** (dati strutturati), Vector DB locali (RAG), CRDT (Conflict-free Replicated Data Types).
- **Ruolo**: Mantenere una base di conoscenza consistente tra i peer senza un database SQL centrale.

### 6. Agent Execution Layer (Reasoning & Planning)
Il motore cognitivo dove risiede la logica applicativa.
- **Tecnologia**: LangGraph, DSPy, Agno, **agentstr-sdk**, **MCP (Model Context Protocol)**.
- **Ruolo**: Orchestrazione dei workflow e delegazione dei task via protocolli Agent-to-Agent.

### 7. Governance & Reputation Layer (Trust)
Il layer di verifica e fiducia sociale.
- **Tecnologia**: **Nostr Web of Trust (WoT)**, firme crittografiche.
- **Ruolo**: Gestire la reputazione basata sul lavoro svolto, permettendo di filtrare i peer in base alla qualità e affidabilità.

---

## Componenti del Monorepo

- **Core (`agentmesh-core`)**: Definisce le interfacce base, l'orchestrazione e le astrazioni LLM/TTS.
- **Relay (`agentmesh-relay`)**: Gestisce l'identità Nostr e la propagazione P2P degli eventi.
- **Vault (`agentmesh-vault`)**: Gestisce l'integrità dei dati tramite IPFS e sistemi di pinning.
- **Applications (`apps/`)**: Casi d'uso reali come **PodcastGen**, che orchestra Content, Storage, Network e Social Agents.

## Strategia di Deduplicazione e Hashing
Per massimizzare il risparmio di risorse (specialmente per il TTS), il sistema utilizza:
1. **Content Hashing**: `hash_input = sha256(urls + voice_id + language + prompt)`.
2. **Verifica Pre-Generazione**: Controllo se il CID dello script o dell'audio esiste già su IPFS/Vault prima di procedere alla generazione AI.
