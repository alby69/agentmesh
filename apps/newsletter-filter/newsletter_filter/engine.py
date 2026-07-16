import logging
from typing import List, Dict, Any, Optional
from newsletter_filter.fetcher import fetch_rss, fetch_imap, ArticleItem
from newsletter_filter.agents.filter_agent import FilterAgent
from agentmesh.core import AgentMessage

logger = logging.getLogger("newsletter_filter.engine")

async def process_filtering(
    source_type: str,
    source_url_or_folder: str,
    criteria: str,
    agent: FilterAgent,
    imap_config: Optional[Dict[str, Any]] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Orchestrates the fetching and filtering pipeline.

    Args:
        source_type: 'rss' or 'imap'
        source_url_or_folder: RSS feed URL or IMAP folder name
        criteria: semantic search criteria/query
        agent: FilterAgent instance
        imap_config: dictionary with host, user, password if source_type is 'imap'
        limit: max articles to fetch
    """
    logger.info(f"Starting pipeline. Source: {source_type} ({source_url_or_folder}), Query: '{criteria}'")

    articles: List[ArticleItem] = []
    if source_type.lower() == "rss":
        articles = await fetch_rss(source_url_or_folder)
    elif source_type.lower() == "imap":
        if not imap_config:
            logger.error("IMAP source requested but no imap_config was provided.")
            return []
        articles = await fetch_imap(
            host=imap_config.get("host", ""),
            user=imap_config.get("user", ""),
            password=imap_config.get("password", ""),
            folder=source_url_or_folder,
            limit=limit
        )
    else:
        logger.error(f"Unsupported source type: {source_type}")
        return []

    logger.info(f"Fetched {len(articles)} articles. Sending to FilterAgent for analysis...")

    filtered_results = []
    for article in articles[:limit]:
        # Construct standardized AgentMessage
        task_msg = AgentMessage(
            sender="pipeline-orchestrator",
            receiver=agent.config.agent_id,
            message_type="task",
            payload={
                "source": article.url,
                "title": article.title,
                "contents": article.content,
                "criteria": criteria
            }
        )

        try:
            # Process via agent's message interface
            response_msg = await agent.handle_message(task_msg)

            # Extract analysis results from payload
            if response_msg.payload.get("status") == "success":
                analysis = response_msg.payload.get("analysis", {})
                filtered_results.append({
                    "title": article.title,
                    "url": article.url,
                    "date": article.date,
                    "analysis": analysis
                })
            else:
                logger.warning(f"FilterAgent rejected or failed to process article: {article.title}")
        except Exception as e:
            logger.error(f"Error executing FilterAgent on {article.title}: {e}")

    return filtered_results
