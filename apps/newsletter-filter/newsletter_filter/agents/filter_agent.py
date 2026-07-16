import json
import logging
from typing import Optional, Dict, Any, List
from agentmesh.core import BaseAgent, MeshConfig, AgentMessage
from agentmesh.llm.base import BaseLLMProvider

logger = logging.getLogger("newsletter_filter.agents.filter_agent")

class FilterAgentConfig(MeshConfig):
    agent_id: str = "newsletter-filter-agent"
    agent_name: str = "Newsletter Filter Agent"
    agent_description: str = "Cognitive Filtering Agent for newsletters and feed contents"
    agent_version: str = "1.0.0"

class FilterAgent(BaseAgent):
    def __init__(self, config: FilterAgentConfig, llm_provider: BaseLLMProvider):
        super().__init__(config)
        self.llm = llm_provider
        self.capabilities = ["newsletter-filtering", "semantic-extraction", "summarization"]

    async def start(self):
        self.logger.info("FilterAgent started.")

    async def stop(self):
        self.logger.info("FilterAgent stopped.")

    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """
        Processes incoming AgentMessages of type 'task' containing 'source' (and contents)
        and 'criteria' to perform cognitive filtering.
        """
        self.logger.info(f"FilterAgent received message type: {message.message_type}")
        if message.message_type == "task":
            source = message.payload.get("source", "unknown")
            contents = message.payload.get("contents", "")
            title = message.payload.get("title", "Untitled")
            criteria = message.payload.get("criteria", "Risorse Umane e AI")

            self.logger.info(f"Filtering content from '{title}' against criteria: '{criteria}'")
            analysis = await self.filter_and_extract(title, contents, criteria)

            # Standardized response message
            return AgentMessage(
                sender=self.config.agent_id,
                receiver=message.sender,
                message_type="response",
                payload={
                    "status": "success",
                    "source": source,
                    "title": title,
                    "analysis": analysis
                }
            )
        else:
            return AgentMessage(
                sender=self.config.agent_id,
                receiver=message.sender,
                message_type="response",
                payload={"status": "ignored", "reason": f"unsupported message_type: {message.message_type}"}
            )

    async def filter_and_extract(self, title: str, content: str, criteria: str) -> Dict[str, Any]:
        """
        Core cognitive processing using agentmesh-llm to extract, score and summarize.
        """
        if not content:
            return {
                "relevant": False,
                "score": 0.0,
                "summary": "Nessun contenuto disponibile da analizzare.",
                "key_points": [],
                "justification": "Contenuto vuoto."
            }

        prompt = f"""
Sei un assistente AI specializzato nel filtraggio cognitivo ed estrazione di informazioni da newsletter e feed.
Analizza il seguente articolo intitolato "{title}" in base ai criteri di ricerca forniti.

Criteri di ricerca semantica: "{criteria}"

Testo dell'articolo:
---
{content}
---

Valuta se l'articolo è rilevante rispetto ai criteri di ricerca.
Fornisci la tua risposta ESCLUSIVAMENTE come un oggetto JSON valido con la seguente struttura, senza alcun testo aggiuntivo, markdown codeblocks o commenti:
{{
  "relevant": true/false (booleano, indica se è significativamente rilevante),
  "score": 0.0-1.0 (decimale, punteggio di rilevanza semantica),
  "summary": "Un riassunto esecutivo in italiano dei punti salienti correlati ai criteri (massimo 150 parole)",
  "key_points": ["Punto chiave 1", "Punto chiave 2", ...],
  "justification": "Una breve spiegazione in italiano del perché l'articolo è rilevante o meno rispetto ai criteri"
}}
"""

        system_instruction = "Sei un analista di testi esperto in grado di estrarre e classificare informazioni e restituire risposte strettamente strutturate in JSON."

        try:
            raw_response = await self.llm.generate(
                prompt=prompt,
                system_instruction=system_instruction
            )
            # Cleanup output in case of markdown wrapping
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            analysis = json.loads(cleaned_response)
            return analysis
        except Exception as e:
            self.logger.error(f"Error during LLM filtering generation or JSON parsing: {e}")
            # Fallback check
            is_relevant_fallback = any(word.lower() in content.lower() for word in criteria.split())
            return {
                "relevant": is_relevant_fallback,
                "score": 0.5 if is_relevant_fallback else 0.0,
                "summary": "Estrazione fallita per errore tecnico. " + content[:200] + "...",
                "key_points": [],
                "justification": f"Errore durante l'elaborazione LLM: {str(e)}"
            }
