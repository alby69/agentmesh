import os
import tempfile
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Set mock db path environment variable before any imports
_temp_dir = tempfile.mkdtemp()
MOCK_DB_PATH = os.path.join(_temp_dir, "test_newsletter_filter.db")
os.environ["FILTER_DB_PATH"] = MOCK_DB_PATH

from fastapi.testclient import TestClient
from newsletter_filter.web.db import (
    init_db, get_db_settings, save_db_settings,
    add_or_update_article, get_articles
)
from newsletter_filter.web.app import app, load_effective_settings


@pytest.fixture(autouse=True)
def setup_teardown_db():
    # Remove mock DB if exists
    if os.path.exists(MOCK_DB_PATH):
        try:
            os.remove(MOCK_DB_PATH)
        except OSError:
            pass

    init_db()
    yield

    # Cleanup after test
    if os.path.exists(MOCK_DB_PATH):
        try:
            os.remove(MOCK_DB_PATH)
        except OSError:
            pass


def test_db_settings_operations():
    # Verify default empty settings
    assert get_db_settings() is None

    # Save settings
    settings_data = {
        "llm_provider": "gemini",
        "llm_model": "gemini-1.5-pro",
        "llm_api_key": "some-key",
        "imap_host": "imap.test.com",
        "imap_user": "test@test.com",
        "imap_password": "secretpassword",
        "imap_folder": "NEWS",
        "rss_urls": "https://test.com/feed,https://test2.com/feed",
        "default_query": "AI in healthcare"
    }
    save_db_settings(settings_data)

    # Read and assert
    saved = get_db_settings()
    assert saved is not None
    assert saved["llm_provider"] == "gemini"
    assert saved["llm_model"] == "gemini-1.5-pro"
    assert saved["imap_folder"] == "NEWS"
    assert saved["rss_urls"] == "https://test.com/feed,https://test2.com/feed"


def test_db_articles_operations():
    # Insert multiple articles with different scores and relevance
    add_or_update_article(
        title="AI Revolution",
        url="https://test.com/ai-rev",
        content="AI is here.",
        date="2026-05-15",
        relevant=True,
        score=0.95,
        summary="Summary AI Rev",
        key_points=["Point 1", "Point 2"],
        justification="Highly relevant"
    )

    add_or_update_article(
        title="Recipe of the day",
        url="https://test.com/recipe",
        content="Pizza recipe.",
        date="2026-05-10",
        relevant=False,
        score=0.10,
        summary="Summary Pizza",
        key_points=[],
        justification="Not relevant"
    )

    # Fetch all articles
    all_art = get_articles()
    assert len(all_art) == 2

    # Fetch only relevant
    rel_art = get_articles(relevant_only=True)
    assert len(rel_art) == 1
    assert rel_art[0]["title"] == "AI Revolution"
    assert rel_art[0]["key_points"] == ["Point 1", "Point 2"]

    # Filter with text search
    searched = get_articles(search_query="Pizza")
    assert len(searched) == 1
    assert searched[0]["title"] == "Recipe of the day"


def test_web_index_and_articles_routes():
    client = TestClient(app)

    # Initial check on home page
    response = client.get("/")
    assert response.status_code == 200
    assert "AgentMesh" in response.text
    assert "Configurazione Attiva" in response.text

    # Populate articles directly to verify list endpoint
    add_or_update_article(
        title="Web AI article",
        url="https://example.com/web-ai",
        content="Testing web.",
        date="2026-05-12",
        relevant=True,
        score=0.85,
        summary="Testing summary.",
        key_points=["Point A"],
        justification="Good relevance"
    )

    response = client.get("/articles")
    assert response.status_code == 200
    assert "Web AI article" in response.text
    assert "RILEVANTE" in response.text

    # Article detail modal
    # First we need the ID
    articles = get_articles()
    art_id = articles[0]["id"]

    response = client.get(f"/article/{art_id}")
    assert response.status_code == 200
    assert "Testing summary." in response.text
    assert "Good relevance" in response.text


def test_web_save_settings_route():
    client = TestClient(app)

    payload = {
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "llm_api_key": "custom-openai-key",
        "default_query": "Nostr protocol and P2P AI",
        "rss_urls": "https://nostr.com/feed",
        "imap_host": "imap.nostr.com",
        "imap_folder": "INBOX",
        "imap_user": "user@nostr.com",
        "imap_password": "nostrpassword"
    }

    response = client.post("/save-settings", data=payload)
    assert response.status_code == 200
    assert "Impostazioni salvate!" in response.text

    # Verify updated settings through DB read
    effective_settings = load_effective_settings()
    assert effective_settings.llm_model == "gpt-4o"
    assert effective_settings.default_query == "Nostr protocol and P2P AI"
    assert effective_settings.rss_urls == ["https://nostr.com/feed"]


def test_web_trigger_scan_and_status():
    client = TestClient(app)

    # Trigger scan
    response = client.post("/trigger-scan", data={"source_type": "rss"})
    assert response.status_code == 200
    assert "Avvio scansione asincrona" in response.text

    # Get job id from the response using string searching
    # response.text should contain hx-get="/check-scan-status/<uuid>"
    import re
    match = re.search(r'/check-scan-status/([a-f0-9\-]+)', response.text)
    assert match is not None
    job_id = match.group(1)

    # Check status (pending/running)
    response_status = client.get(f"/check-scan-status/{job_id}")
    assert response_status.status_code == 200
    assert "Scansione in corso" in response_status.text or "completata con successo" in response_status.text


@pytest.mark.asyncio
async def test_web_export_podcast_api():
    client = TestClient(app)

    # Prepare mocked endpoint response for Podcast Generator API
    # Since we use httpx AsyncClient in export_podcast_route, we can patch it
    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 200
    mock_post_resp.json.return_value = {"status": "success", "job_id": "mock-job-xyz123"}

    # Mock the AsyncClient.post function
    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_post_resp)) as mock_post:
        payload = {
            "urls": ["https://example.com/article-1", "https://example.com/article-2"]
        }

        response = client.post("/export-podcast", json=payload)
        assert response.status_code == 200
        assert "Esportato con successo a Podcast Generator!" in response.text
        assert "mock-job-xyz123" in response.text

        # Verify the outgoing payload
        mock_post.assert_called_once()
        called_args, called_kwargs = mock_post.call_args
        assert called_kwargs["json"] == {"urls": ["https://example.com/article-1", "https://example.com/article-2"]}
