# PodcastGen 3.0: Visione e Filosofia

Questo documento consolida le proposte per la versione 3.0, definendo PodcastGen non più come un semplice tool, ma come un ecosistema **Agente-Centrico e Decentralizzato**.

## 1. La Filosofia P2P (Peer-to-Peer)
PodcastGen 3.0 elimina la necessità di un server centrale. L'applicazione vive sui dispositivi degli utenti e comunica attraverso protocolli aperti, garantendo sovranità sui dati e resistenza alla censura.

### I Tre Pilastri
| Pilastro | Tecnologia | Scopo |
| :--- | :--- | :--- |
| **Identità & Social** | **Nostr** | Gestione chiavi (pub/priv), discovery di peer, commenti e bacheche senza server. |
| **Archiviazione** | **IPFS** | Storage "content-addressed". I file audio sono identificati dal loro Hash (CID) e distribuiti globalmente. |
| **Intelligenza** | **Multi-Agent** | Una flotta di agenti specializzati che orchestrano il flusso di lavoro (Content, Storage, Network, Social). |

---

## 2. Architettura Multi-Agente
Seguendo la visione di Andrej Karpathy, PodcastGen è un'orchestra di agenti coordinati:

1.  **Network Agent:** Gestisce la connessione ai relay Nostr e la pubblicazione di eventi standardizzati (NIP-94).
2.  **Storage Agent:** Gestisce l'integrità e la disponibilità dei dati tramite IPFS, con supporto per Pinata e nodi locali.
3.  **Content Agent:** L'agente creativo. Esegue fetch, traduzione (LLM) e sintesi (TTS).
4.  **Social Agent:** Gestisce il feed della community, i like e le reaction basate su eventi Nostr.

---

## 3. Il Modello di Comunità Sovrana
A differenza dei social network tradizionali, PodcastGen 3.0 non raccoglie dati:
- **Zero Costi Server:** Gli utenti contribuiscono con la loro banda e spazio (volontariamente).
- **Privacy Totale:** I messaggi sono firmati crittograficamente e possono essere criptati E2E.
- **Deduplicazione Nativa:** Se due utenti generano lo stesso podcast, IPFS riconosce l'hash identico e non duplica lo spazio occupato.

---

## 4. Evoluzione Social
Le funzionalità social (chat, gruppi) vengono realizzate tramite i relay Nostr, rendendo la piattaforma compatibile con l'intero ecosistema Nostr (Damus, Amethyst, ecc.).

> "Il futuro del podcasting non è una piattaforma, è un protocollo."
