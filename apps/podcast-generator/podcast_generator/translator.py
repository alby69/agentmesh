from __future__ import annotations

from podcast_generator.config import Settings
from podcast_generator.exceptions import TranslationError
from agentmesh.llm import LLMProviderFactory, BaseLLMProvider

LANGUAGE_SYSTEM_PROMPT = """Sei un autore e conduttore di podcast tecnologici.
Il tuo compito è prendere una o più newsletter tecniche in inglese e trasformarle
in un coinvolgente script per un podcast in {language}.

REGOLE:
- Traduci in {language}, ma adatta il tono all'ascolto: colloquiale, dinamico, entusiasta
- Non elencare i tool in modo freddo: presentali con transizioni naturali
- Se ci sono più newsletter, uniscile in un unico episodio settimanale
  creando macro-categorie e rimuovendo duplicati
- Inizia direttamente con un saluto appropriato nella lingua di destinazione
- Non aggiungere NOTE, INTRODUZIONI o commenti meta (es. "Ecco lo script")
- Produci solo il testo da leggere, senza markup o istruzioni di regia
- Ogni episodio deve essere un monologo fluido e piacevole da ascoltare"""

DIALOGUE_SYSTEM_PROMPT = """Sei un team di due podcaster (Host e Guest).
Il tuo compito è prendere una o più newsletter tecniche in inglese e trasformarle
in una conversazione coinvolgente (stile NotebookLM) in {language}.

REGOLE:
- Traduci in {language}, ma mantieni un tono colloquiale e serrato tra i due conduttori.
- Formato: [Host]: ... [Guest]: ... [Host]: ...
- L'Host introduce gli argomenti e guida la discussione.
- Il Guest approfondisce i dettagli, fa domande intelligenti e reagisce con entusiasmo.
- Non elencare i tool: discutili come se li steste scoprendo insieme.
- Inizia direttamente con un saluto tra i due conduttori.
- Produci solo il testo del dialogo con i tag [Host] e [Guest], senza markup aggiuntivo.
- Ogni episodio deve essere un dialogo fluido, naturale e piacevole da ascoltare."""


def build_system_prompt(language: str, format: str = "monologue") -> str:
    if format == "dialogue":
        return DIALOGUE_SYSTEM_PROMPT.format(language=language)
    return LANGUAGE_SYSTEM_PROMPT.format(language=language)


def get_llm_provider(cfg: Settings) -> BaseLLMProvider:
    try:
        if cfg.llm_provider == "gemini":
            return LLMProviderFactory.create("gemini", api_key=cfg.gemini_api_key, default_model=cfg.gemini_model)
        elif cfg.llm_provider == "openai":
            return LLMProviderFactory.create("openai", api_key=cfg.openai_api_key, default_model=cfg.openai_model)
        elif cfg.llm_provider == "anthropic":
            return LLMProviderFactory.create("anthropic", api_key=cfg.anthropic_api_key, default_model=cfg.anthropic_model)
        elif cfg.llm_provider == "ollama":
            return LLMProviderFactory.create("ollama", base_url=cfg.ollama_base_url, default_model=cfg.ollama_model)
        else:
            raise TranslationError(f"Unknown LLM provider '{cfg.llm_provider}'")
    except Exception as e:
        raise TranslationError(f"Failed to initialize LLM provider: {e}") from e


async def translate_newsletter(
    cfg: Settings, text: str
) -> str:
    provider = get_llm_provider(cfg)
    system_prompt = build_system_prompt(cfg.language, cfg.podcast_format)

    kwargs = {}
    if cfg.use_web_search and cfg.llm_provider == "gemini":
        kwargs["tools"] = [{"google_search": {}}]

    if cfg.use_web_search:
        prompt = (
            f"Testo da convertire in podcast in {cfg.language}:\n\n{text}\n\n"
            "IMPORTANTE: Usa Google Search per approfondire ogni notizia citata, "
            "aggiungendo dettagli tecnici, contesto e curiosità recenti."
        )
    else:
        prompt = f"Testo da convertire in podcast in {cfg.language}:\n\n{text}"

    return await provider.generate(prompt, system_instruction=system_prompt, **kwargs)


async def translate_multiple(
    cfg: Settings, newsletters: list[tuple[str, str]]
) -> str:
    provider = get_llm_provider(cfg)
    system_prompt = build_system_prompt(cfg.language, cfg.podcast_format)

    combined = "\n\n--- NUOVA NEWSLETTER ---\n\n".join(
        f"TITOLO: {title}\nTESTO:\n{content}"
        for title, content in newsletters
    )

    prompt = (
        "Qui ci sono PIU' newsletter da unire in un unico episodio podcast "
        "settimanale. Riorganizzale per argomento, elimina duplicati e crea "
        f"un monologo fluido in {cfg.language}.\n\n"
        f"{combined}"
    )

    kwargs = {}
    if cfg.use_web_search and cfg.llm_provider == "gemini":
        kwargs["tools"] = [{"google_search": {}}]

    if cfg.use_web_search:
        prompt += (
            "\n\nIMPORTANTE: Usa Google Search per approfondire gli argomenti principali, "
            "aggiungendo dettagli tecnici e contesto aggiornato."
        )

    return await provider.generate(prompt, system_instruction=system_prompt, **kwargs)
