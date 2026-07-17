import asyncio
import logging
from typing import List, Dict, Any, Optional
from newsletter_filter.fetcher import fetch_rss, fetch_imap, ArticleItem
from newsletter_filter.agents.filter_agent import FilterAgent
from agentmesh.core import AgentMessage

logger = logging.getLogger("newsletter_filter.engine")

DEFAULT_MAX_CONCURRENT = 3


async def _process_one_article(
    article: ArticleItem,
    criteria: str,
    agent: FilterAgent,
    semaphore: asyncio.Semaphore,
) -> Optional[Dict[str, Any]]:
    task_msg = AgentMessage(
        sender="pipeline-orchestrator",
        receiver=agent.config.agent_id,
        message_type="task",
        payload={
            "source": article.url,
            "title": article.title,
            "contents": article.content,
            "criteria": criteria,
        },
    )

    async with semaphore:
        try:
            response_msg = await agent.handle_message(task_msg)
            if response_msg.payload.get("status") == "success":
                analysis = response_msg.payload.get("analysis", {})
                return {
                    "title": article.title,
                    "url": article.url,
                    "date": article.date,
                    "analysis": analysis,
                }
            logger.warning("FilterAgent rejected article: %s", article.title)
        except Exception as e:
            logger.error("Error processing %s: %s", article.title, e)
    return None


async def process_filtering(
    source_type: str,
    source_url_or_folder: str,
    criteria: str,
    agent: FilterAgent,
    imap_config: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    substack_limit: int = 0,
    substack_offset: int = 0,
) -> List[Dict[str, Any]]:
    logger.info(
        "Starting pipeline. Source: %s (%s), Query: '%s'",
        source_type, source_url_or_folder, criteria,
    )

    articles: List[ArticleItem] = []
    if source_type.lower() == "rss":
        articles = await fetch_rss(
            source_url_or_folder,
            substack_limit=substack_limit,
            substack_offset=substack_offset,
        )
    elif source_type.lower() == "imap":
        if not imap_config:
            logger.error("IMAP source requested but no imap_config was provided.")
            return []
        articles = await fetch_imap(
            host=imap_config.get("host", ""),
            user=imap_config.get("user", ""),
            password=imap_config.get("password", ""),
            folder=source_url_or_folder,
            limit=limit,
        )
    else:
        logger.error("Unsupported source type: %s", source_type)
        return []

    logger.info("Fetched %d articles. Analyzing with %d concurrent workers...", len(articles), max_concurrent)

    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [
        _process_one_article(article, criteria, agent, semaphore)
        for article in articles[:limit]
    ]
    results = await asyncio.gather(*tasks)

    return [r for r in results if r is not None]
