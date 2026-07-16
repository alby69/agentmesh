import feedparser
import trafilatura
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

logger = logging.getLogger("newsletter_filter.fetcher")

class ArticleItem:
    def __init__(self, title: str, content: str, url: str, date: Optional[str] = None):
        self.title = title
        self.content = content
        self.url = url
        self.date = date or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "date": self.date
        }

async def fetch_rss(url: str) -> List[ArticleItem]:
    """
    Fetches articles from an RSS feed and extracts their body content.
    """
    logger.info(f"Fetching RSS feed from: {url}")
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        logger.error(f"Error parsing RSS feed {url}: {e}")
        return []

    articles = []
    for entry in feed.entries:
        title = entry.get("title", "No Title")
        link = entry.get("link", "")
        published = entry.get("published", "")

        # Try to extract content directly or fallback to downloading url
        content = ""
        if "content" in entry:
            # RSS entry content blocks
            content_html = entry.content[0].value
            content = trafilatura.extract(content_html) or ""

        if not content and "summary" in entry:
            content = trafilatura.extract(entry.summary) or entry.summary

        if not content and link:
            # Fallback download using trafilatura
            try:
                downloaded = trafilatura.fetch_url(link)
                if downloaded:
                    content = trafilatura.extract(downloaded) or ""
            except Exception as e:
                logger.warning(f"Failed to fetch content via URL {link}: {e}")

        if content:
            articles.append(ArticleItem(title=title, content=content, url=link, date=published))

    return articles

async def fetch_imap(
    host: str, user: str, password: str, folder: str = "INBOX", limit: int = 10
) -> List[ArticleItem]:
    """
    Fetches recent emails from an IMAP folder using imap-tools.
    """
    if not host or not user or not password:
        logger.warning("IMAP credentials not completely set. Skipping IMAP fetch.")
        return []

    logger.info(f"Connecting to IMAP {host} and checking {folder}")
    try:
        from imap_tools import MailBox, AND
    except ImportError:
        logger.error("imap-tools package is required for IMAP fetching.")
        return []

    articles = []
    try:
        with MailBox(host).login(user, password) as mailbox:
            mailbox.folder.set(folder)
            # Fetch last `limit` messages sorted descending by UID/ID
            messages = list(mailbox.fetch(AND(all=True), limit=limit, reverse=True))
            for msg in messages:
                subject = msg.subject
                # extract content from HTML body
                body_content = ""
                if msg.html:
                    body_content = trafilatura.extract(msg.html) or ""
                if not body_content and msg.text:
                    body_content = msg.text

                url = f"email://{msg.uid}"
                date_str = msg.date.isoformat() if msg.date else None
                articles.append(ArticleItem(title=subject, content=body_content, url=url, date=date_str))
    except Exception as e:
        logger.error(f"IMAP fetch error: {e}")

    return articles
