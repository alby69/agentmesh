import asyncio
import json
import logging
import subprocess
from typing import List

import trafilatura

from newsletter_filter.fetcher import ArticleItem

logger = logging.getLogger("newsletter_filter.fetcher_substack")

ARCHIVE_PAGE_SIZE = 25
DEFAULT_MAX_POSTS = 500
REQUEST_DELAY = 0.3


def _is_substack_url(url: str) -> bool:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.hostname == "substack.com" or (
        parsed.hostname and parsed.hostname.endswith(".substack.com")
    )


def _base_url(feed_url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(feed_url)
    return f"{parsed.scheme}://{parsed.hostname}"


def _curl_json(url: str, retries: int = 2) -> list | dict | None:
    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", "30", url],
                capture_output=True, text=True, timeout=35,
            )
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except Exception as e:
            logger.warning("curl failed for %s (attempt %d): %s", url, attempt + 1, e)
        if attempt < retries:
            import time
            time.sleep(1)
    return None


def _fetch_archive_page(base: str, offset: int, limit: int) -> List[dict]:
    data = _curl_json(f"{base}/api/v1/archive?offset={offset}&limit={limit}")
    return data if isinstance(data, list) else []


def _fetch_post_body(base: str, slug: str) -> str:
    data = _curl_json(f"{base}/api/v1/posts/{slug}")
    if isinstance(data, dict):
        html = data.get("body_html") or ""
        if html:
            return trafilatura.extract(html) or ""
    return ""


async def fetch_substack(
    feed_url: str,
    limit: int = DEFAULT_MAX_POSTS,
    offset: int = 0,
) -> List[ArticleItem]:
    base = _base_url(feed_url)
    logger.info("Fetching Substack archive from %s (limit=%s, offset=%s)", base, limit, offset)

    articles: List[ArticleItem] = []
    fetched_slugs: set[str] = set()
    current_offset = offset
    remaining = limit if limit > 0 else None

    while True:
        page_size = min(ARCHIVE_PAGE_SIZE, remaining) if remaining is not None else ARCHIVE_PAGE_SIZE
        posts = _fetch_archive_page(base, current_offset, page_size)

        if not posts:
            break

        for post in posts:
            slug = post.get("slug", "")
            if not slug or slug in fetched_slugs:
                continue

            title = post.get("title", "No Title")
            post_date = post.get("post_date", "")
            canonical_url = post.get("canonical_url") or f"{base}/p/{slug}"
            description = post.get("description") or post.get("truncated_body_text") or ""

            content = ""
            has_full_body = False

            body_html = post.get("body_html")
            if body_html:
                extracted = trafilatura.extract(body_html) or ""
                if extracted:
                    content = extracted
                    has_full_body = True

            if not has_full_body:
                await asyncio.sleep(REQUEST_DELAY)
                content = _fetch_post_body(base, slug)

            if not content and description:
                content = description

            if content:
                articles.append(ArticleItem(
                    title=title,
                    content=content,
                    url=canonical_url,
                    date=post_date,
                ))
                fetched_slugs.add(slug)

            if remaining is not None:
                remaining -= 1
                if remaining <= 0:
                    break

        if remaining is not None and remaining <= 0:
            break

        current_offset += page_size
        await asyncio.sleep(REQUEST_DELAY)

    logger.info("Fetched %d articles from Substack archive", len(articles))
    return articles
