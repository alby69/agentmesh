import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from feedparser import FeedParserDict
from newsletter_filter.fetcher import ArticleItem, fetch_rss, fetch_imap
from newsletter_filter.agents.filter_agent import FilterAgent, FilterAgentConfig
from newsletter_filter.engine import process_filtering
from agentmesh.core import AgentMessage
from agentmesh.llm.base import BaseLLMProvider

def test_article_item_to_dict():
    item = ArticleItem(
        title="Test Title",
        content="Test Content",
        url="https://test.com/1",
        date="2026-05-15"
    )
    d = item.to_dict()
    assert d["title"] == "Test Title"
    assert d["content"] == "Test Content"
    assert d["url"] == "https://test.com/1"
    assert d["date"] == "2026-05-15"

@pytest.mark.asyncio
async def test_fetch_rss_mock():
    # Use feedparser FeedParserDict to mock entry with both dict and attribute access
    mock_entry = FeedParserDict({
        "title": "Mock Post",
        "link": "https://mock.com/post-1",
        "published": "2026-05-10",
        "summary": "This is a mock newsletter summary."
    })
    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]

    with patch("feedparser.parse", return_value=mock_feed):
        # Patch trafilatura.extract to return the content we want
        with patch("trafilatura.extract", return_value="This is a mock newsletter summary."):
            articles = await fetch_rss("https://mock.com/feed")
            assert len(articles) == 1
            assert articles[0].title == "Mock Post"
            assert articles[0].content == "This is a mock newsletter summary."
            assert articles[0].url == "https://mock.com/post-1"

@pytest.mark.asyncio
async def test_fetch_imap_mock():
    # Mock MailBox in imap-tools
    mock_msg = MagicMock()
    mock_msg.subject = "Email Subject"
    mock_msg.html = "<html><body>Email Body HTML</body></html>"
    mock_msg.text = "Email Body Text"
    mock_msg.uid = "123"
    mock_msg.date = MagicMock()
    mock_msg.date.isoformat.return_value = "2026-05-12T10:00:00"

    mock_mailbox_instance = MagicMock()
    # mailbox.login(...) must return mock_mailbox_instance so __enter__ works correctly on it
    mock_mailbox_instance.login.return_value = mock_mailbox_instance
    mock_mailbox_instance.__enter__.return_value = mock_mailbox_instance
    mock_mailbox_instance.folder.set = MagicMock()
    mock_mailbox_instance.fetch.return_value = [mock_msg]

    with patch("imap_tools.MailBox", return_value=mock_mailbox_instance):
        with patch("trafilatura.extract", return_value="Email Body Text"):
            articles = await fetch_imap(
                host="imap.mock.com",
                user="user@mock.com",
                password="password",
                folder="INBOX",
                limit=5
            )
            assert len(articles) == 1
            assert articles[0].title == "Email Subject"
            assert articles[0].content == "Email Body Text"
            assert articles[0].url == "email://123"

@pytest.mark.asyncio
async def test_filter_agent_filter_and_extract():
    # Mock LLM provider
    mock_llm = MagicMock(spec=BaseLLMProvider)

    mock_response = {
        "relevant": True,
        "score": 0.95,
        "summary": "Riassunto dell'impatto dell'AI sulle risorse umane.",
        "key_points": ["Punto 1", "Punto 2"],
        "justification": "Spiegazione della rilevanza semantica."
    }

    mock_llm.generate = AsyncMock(return_value=json.dumps(mock_response))

    config = FilterAgentConfig()
    agent = FilterAgent(config, mock_llm)

    result = await agent.filter_and_extract(
        title="HR & AI Integration",
        content="Artificial intelligence is transforming resources management.",
        criteria="AI and HR"
    )

    assert result["relevant"] is True
    assert result["score"] == 0.95
    assert "Riassunto" in result["summary"]
    assert len(result["key_points"]) == 2

@pytest.mark.asyncio
async def test_filter_agent_handle_message():
    mock_llm = MagicMock(spec=BaseLLMProvider)
    mock_response = {
        "relevant": False,
        "score": 0.1,
        "summary": "Non correlato.",
        "key_points": [],
        "justification": "Non parla di HR."
    }
    mock_llm.generate = AsyncMock(return_value=json.dumps(mock_response))

    config = FilterAgentConfig()
    agent = FilterAgent(config, mock_llm)

    # Test handling 'task' AgentMessage
    task_msg = AgentMessage(
        sender="sender-id",
        receiver="newsletter-filter-agent",
        message_type="task",
        payload={
            "source": "https://test.com/abc",
            "title": "Random post",
            "contents": "Just some food recipes.",
            "criteria": "Risorse Umane"
        }
    )

    resp_msg = await agent.handle_message(task_msg)
    assert resp_msg.message_type == "response"
    assert resp_msg.payload["status"] == "success"
    assert resp_msg.payload["analysis"]["relevant"] is False
    assert resp_msg.payload["analysis"]["score"] == 0.1

@pytest.mark.asyncio
async def test_process_filtering_engine():
    mock_llm = MagicMock(spec=BaseLLMProvider)
    mock_response = {
        "relevant": True,
        "score": 0.88,
        "summary": "Analisi dell'evoluzione HR.",
        "key_points": ["Evoluzione"],
        "justification": "Punti salienti rilevati."
    }
    mock_llm.generate = AsyncMock(return_value=json.dumps(mock_response))

    config = FilterAgentConfig()
    agent = FilterAgent(config, mock_llm)

    # Mock fetch_rss to return mock articles
    mock_articles = [
        ArticleItem(title="AI HR", content="Contenuto AI", url="https://mock.com/1")
    ]

    with patch("newsletter_filter.engine.fetch_rss", AsyncMock(return_value=mock_articles)):
        results = await process_filtering(
            source_type="rss",
            source_url_or_folder="https://mock.com/feed",
            criteria="AI HR",
            agent=agent,
            limit=5
        )

        assert len(results) == 1
        assert results[0]["title"] == "AI HR"
        assert results[0]["analysis"]["relevant"] is True
        assert results[0]["analysis"]["score"] == 0.88
