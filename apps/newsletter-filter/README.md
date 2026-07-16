# Newsletter Filter & Extraction App / Agent (v4.0.1)

Questa applicazione fa parte del monorepo di **AgentMesh** e fornisce uno strumento asincrono e cognitivo per il filtraggio di newsletter ed estrazione di contenuti rilevanti in base a keyword e criteri di ricerca semantica.

## Funzionalità
- **IMAP Client**: Scaricamento e parsing di email da qualsiasi casella di posta (es. Gmail/Substack).
- **RSS Feed Reader**: Lettura di feed RSS pubblici e parsing con `feedparser` e `trafilatura`.
- **Cognitive Agent**: Il `FilterAgent` utilizza `agentmesh-llm` per analizzare la rilevanza semantica e strutturare i concetti.
- **Interfaccia Standard**: Utilizza i protocolli e i messaggi standard del framework (`AgentMessage` e `BaseAgent`).

## Requisiti
Le dipendenze del framework `agentmesh-core`, `agentmesh-llm`, ecc. vengono risolte tramite `uv` workspace.

## Utilizzo CLI
```bash
# Esegui il filtraggio tramite riga di comando
PYTHONPATH=. uv run main.py --source "https://stefanogatti.substack.com/feed" --query "Risorse Umane e AI"
```
