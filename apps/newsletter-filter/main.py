import asyncio
import argparse
import json
import sys
import os
import logging
from newsletter_filter.config import FilterSettings
from newsletter_filter.agents.filter_agent import FilterAgent, FilterAgentConfig
from newsletter_filter.engine import process_filtering
from agentmesh.llm.factory import LLMProviderFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("newsletter_filter.main")

async def main_async():
    parser = argparse.ArgumentParser(
        description="Newsletter Filter & Extraction CLI tool (AgentMesh App)"
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Start the FastAPI HTMX Web Server instead of CLI"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind the web server to (default: 8001)"
    )
    parser.add_argument(
        "--source-type",
        choices=["rss", "imap"],
        default="rss",
        help="Type of content source: 'rss' or 'imap' (default: 'rss')"
    )
    parser.add_argument(
        "--source",
        type=str,
        help="RSS URL or IMAP folder name (e.g. 'INBOX'). If not specified, default RSS feeds will be used."
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Semantic search criteria/query. If not specified, default query from config will be used."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of articles/emails to fetch and process (default: 5)"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format: 'text' (default) or 'json'"
    )

    args = parser.parse_args()

    if args.server:
        import uvicorn
        logger.info(f"Starting Newsletter Filter Web Server on port {args.port}...")
        uvicorn.run("newsletter_filter.web.app:app", host="0.0.0.0", port=args.port, reload=True)
        return

    # Load settings from environment variables/dotenv file
    settings = FilterSettings()

    source_type = args.source_type
    query = args.query or settings.default_query
    limit = args.limit

    # Resolve source
    source = args.source
    if not source:
        if source_type == "rss":
            if settings.rss_urls:
                source = settings.rss_urls[0]
            else:
                # Default to Stefano Gatti's RSS feed as a great starting point!
                source = "https://stefanogatti.substack.com/feed"
        else:
            source = settings.imap_folder or "INBOX"

    logger.info(f"Using Provider: {settings.llm_provider}, Model: {settings.llm_model}")

    # Initialize LLM Provider
    api_key = settings.llm_api_key or os.getenv("OPENAI_API_KEY") or "mock-key"
    try:
        llm_provider = LLMProviderFactory.create(
            settings.llm_provider,
            api_key=api_key,
            default_model=settings.llm_model
        )
    except Exception as e:
        logger.error(f"Failed to create LLM Provider: {e}")
        sys.exit(1)

    # Initialize Filter Agent
    agent_config = FilterAgentConfig()
    agent = FilterAgent(agent_config, llm_provider)

    # Prepare IMAP config if needed
    imap_config = None
    if source_type == "imap":
        imap_config = {
            "host": settings.imap_host,
            "user": settings.imap_user,
            "password": settings.imap_password
        }
        if not imap_config["host"] or not imap_config["user"]:
            logger.error("IMAP host or user is missing. Please set FILTER_IMAP_HOST and FILTER_IMAP_USER.")
            sys.exit(1)

    # Execute filtering pipeline
    results = await process_filtering(
        source_type=source_type,
        source_url_or_folder=source,
        criteria=query,
        agent=agent,
        imap_config=imap_config,
        limit=limit
    )

    # Output formatted report
    if args.output == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("\n" + "="*80)
    print("COGNITIVE NEWSLETTER FILTERING REPORT")
    print(f"Source Type: {source_type.upper()}")
    print(f"Source:      {source}")
    print(f"Criteria:    '{query}'")
    print("="*80 + "\n")

    relevant_count = 0
    for idx, item in enumerate(results, 1):
        analysis = item.get("analysis", {})
        relevant = analysis.get("relevant", False)
        score = analysis.get("score", 0.0)

        status_str = "🟢 [RILEVANTE]" if relevant else "🔴 [NON RILEVANTE]"

        print(f"{idx}. {item['title']}")
        print(f"   URL:   {item['url']}")
        print(f"   Stato: {status_str} (Punteggio di rilevanza semantica: {score:.2f})")
        print(f"   Spiegazione: {analysis.get('justification', '')}")

        if relevant:
            relevant_count += 1
            print("   Sintesi:")
            print(f"     {analysis.get('summary', '')}")
            points = analysis.get("key_points", [])
            if points:
                print("   Punti Chiave:")
                for pt in points:
                    print(f"     - {pt}")
        print("-" * 80)

    print(f"\nPipeline terminata. Trovati {relevant_count} articoli rilevanti su {len(results)} analizzati.\n")

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")

if __name__ == "__main__":
    main()
