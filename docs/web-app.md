# Podcast Generator — Web App

Web app to generate podcasts from newsletters with a visual interface and REST API.

> [!WARNING]
> **Version 3.0 (In Development):** The current web interface interacts with a local SQLite database. We are migrating towards a decentralized UI that queries **Nostr** relays and retrieves audio from **IPFS**.

## Quick Start

```bash
source .venv/bin/activate

# Start the server
uvicorn podcast_generator.web.app:app --reload

# Or with custom parameters
uvicorn podcast_generator.web.app:app --host 0.0.0.0 --port 8080 --reload
```

Open http://localhost:8000

## Example: Beehiiv Newsletter

### 1. Configure `.env`

```env
GEMINI_API_KEY=AIza...
TTS_VOICE=it-IT-ElsaNeural

# No need to configure NEWSLETTER_URL here —
# you will enter it directly from the web UI
```

### 2. Start the server

```bash
uvicorn podcast_generator.web.app:app --reload
```

### 3. Use the Web UI

1. Open http://localhost:8000
2. Choose the source:
   - **Web**: paste newsletter URL (e.g., `https://newsletter.theresanaiforthat.com`) and click **Analyze**
   - **Email**: go to **Settings**, configure IMAP (host, user, password, folder), return home and click **Analyze**
3. You will see the list of articles with checkboxes
4. Select one or more articles
5. Click **"Generate Podcast"**
6. Wait for generation (HTMX polling shows progress)
7. Download the MP3 or listen from the embedded player

### 4. Use the REST API

```bash
# 1. Get article list
curl -X POST http://localhost:8000/api/v1/fetch-articles \
  -H "Content-Type: application/json" \
  -d '{"url": "https://newsletter.theresanaiforthat.com"}'

# 2. Start generation
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://newsletter.theresanaiforthat.com/p/article-1"]}'
# → {"job_id": "abc123", "status": "processing", "status_url": "/api/v1/status/abc123"}

# 3. Check status
curl http://localhost:8000/api/v1/status/abc123
# → {"job_id": "abc123", "status": "completed", "download_url": "/download/daily/...mp3", ...}

# 4. Download
curl -O http://localhost:8000/api/v1/episodes/1/audio
```

## Authentication

### OAuth (Google / GitHub)

Recommended method. Create an OAuth Client ID in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
or [GitHub Settings](https://github.com/settings/developers) and set it in `.env`:

```env
OAUTH_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
OAUTH_GOOGLE_CLIENT_SECRET=GOCSPX-...
# OAUTH_GITHUB_CLIENT_ID=xxx
# OAUTH_GITHUB_CLIENT_SECRET=xxx
JWT_SECRET=a-random-key-at-least-32-characters
```

**Callback URI to register:** `http://localhost:8000/auth/callback`

### Shared Password (fallback)

If you don't configure OAuth, you can use a single password:

```env
WEB_PASSWORD=my-secure-password
```

The login page will show the password form. The `session` cookie expires after 7 days.

### Development Mode

If you configure neither OAuth nor `WEB_PASSWORD`, access is open (useful in development).

### REST API (Bearer token)

```env
API_TOKEN=my-api-token
```

All `/api/v1/*` endpoints now require:

```bash
curl -H "Authorization: Bearer my-api-token" http://localhost:8000/api/v1/episodes
```

If `API_TOKEN` is empty (default), APIs are public.

### Auth Variables Summary

| Variable | Default | Role |
|---|---|---|
| `OAUTH_GOOGLE_CLIENT_ID` | — | Google OAuth Client ID |
| `OAUTH_GOOGLE_CLIENT_SECRET` | — | Google OAuth Client Secret |
| `OAUTH_GITHUB_CLIENT_ID` | — | GitHub OAuth Client ID |
| `OAUTH_GITHUB_CLIENT_SECRET` | — | GitHub OAuth Client Secret |
| `JWT_SECRET` | `change-me` | HMAC key for JWT session signing |
| `WEB_PASSWORD` | — | Web UI fallback password |
| `API_TOKEN` | — | REST API token (empty = public) |

## API Endpoints

### Web UI

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | Session | Home page |
| GET | `/login` | — | Login page (OAuth + password) |
| POST | `/login` | — | Password login |
| GET | `/logout` | — | Logout |
| GET | `/auth/google` | — | Google OAuth redirect |
| GET | `/auth/github` | — | GitHub OAuth redirect |
| GET | `/auth/callback` | — | OAuth callback |
| POST | `/fetch-articles` | Session | Extract articles from URL/email |
| POST | `/fetch-more-emails` | Session | Load more IMAP emails |
| POST | `/article` | Session | Article detail |
| POST | `/generate` | Session | Start podcast generation |
| GET | `/check-status/{job_id}` | Session | Generation status polling |
| GET | `/settings` | Session | Settings page |
| POST | `/save-settings` | Session | Save settings |
| GET | `/imap-folders` | Session | List IMAP folders |
| POST | `/imap-debug` | Session | Gmail label debug |
| GET | `/download/{folder}/{file}` | Public | MP3 download |
| GET | `/rss` | Public | Episode RSS feed |

### REST API (all `/api/v1/*`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/generate` | Bearer | Start podcast generation |
| GET | `/api/v1/status/{job_id}` | Bearer | Generation status |
| GET | `/api/v1/episodes` | Bearer | Episode list (`?limit=20`) |
| GET | `/api/v1/episodes/{id}` | Bearer | Episode detail |
| GET | `/api/v1/episodes/{id}/audio` | Bearer | MP3 file download |
| POST | `/api/v1/fetch-articles` | Bearer | Article list from URL |

## Detailed API Reference

### `POST /api/v1/generate`

Request:
```json
{
    "urls": ["https://example.com/p/article-1", "https://example.com/p/article-2"]
}
```

Response (202):
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "status_url": "/api/v1/status/550e8400-e29b-41d4-a716-446655440000"
}
```

### `GET /api/v1/status/{job_id}`

Response:
```json
{
    "job_id": "550e8400-...",
    "status": "completed",
    "download_url": "/download/daily/2026-05-27_title_abc123.mp3",
    "title": "AI News",
    "filename": "2026-05-27_title_abc123.mp3"
}
```

Possible statuses: `pending`, `processing`, `completed`, `failed`.

### `GET /api/v1/episodes`

Response:
```json
[
    {
        "id": 1,
        "title": "AI News",
        "url": "https://example.com/p/article",
        "date": "2026-05-27",
        "audio_path": "/download/daily/2026-05-27_title.mp3",
        "script_path": "./output/daily/2026-05-27_title.txt",
        "created_at": "2026-05-27T10:00:00"
    }
]
```

### `POST /api/v1/fetch-articles`

Request:
```json
{
    "url": "https://newsletter.theresanaiforthat.com"
}
```

Response:
```json
{
    "articles": [
        {
            "href": "https://.../p/ai-framework-xyz",
            "text": "AI Framework XYZ 5.0",
            "description": "New AI framework..."
        }
    ]
}
```

## Swagger UI

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## RSS Feed

`GET /rss` produces an RSS 2.0 feed compatible with Apple Podcasts, Spotify, and any podcast player.

```
http://localhost:8000/rss
```

To expose it publicly, use a reverse proxy (nginx, Caddy) or a service like ngrok.

## Docker Deployment

```bash
# Build
docker build -t podcast-generator .

# Run
docker run -d \
  --name podcast-gen \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/output:/app/output \
  podcast-generator
```

With Docker Compose:

```yaml
version: "3.8"
services:
  podcast-gen:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./.env:/app/.env
      - ./output:/app/output
    restart: unless-stopped
```

## Reverse Proxy Deployment (nginx)

```nginx
server {
    listen 80;
    server_name podcast.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }

    location /download/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_read_timeout 600s;
    }
}
```

## Email Source (IMAP)

Configurable from the **Settings** page (`/settings`) or via `.env`.

### Gmail

To use Gmail, an **App Password** is required:

1. Enable [2-step verification](https://myaccount.google.com/security)
2. Generate an [App Password](https://myaccount.google.com/apppasswords) for "Mail"
3. Enter the details:
   - **Host**: `imap.gmail.com`
   - **User**: `your.email@gmail.com`
   - **Password**: the generated App Password
   - **Folder**: `INBOX` or a Gmail label (e.g., `Newsletter/TAAFT`)

### IMAP via Web UI

1. Go to **Settings** (top right)
2. Fill in the IMAP fields
3. Click **"List available folders"** to explore labels
4. Select a folder and save
5. Return home and click **"Analyze"**

### Behavior

- **100 emails** per batch (configurable 1-1000 via `IMAP_MAX_EMAILS`)
- **"Load more emails"** button loads the next batch
- RFC 2047 decoded subjects
- Detail view with HTML content of the newsletter

## Production Security Tips

1. **Configure OAuth** (Google/GitHub) instead of `WEB_PASSWORD`
2. **Change `JWT_SECRET`** with a random key (at least 32 characters)
3. **Set `API_TOKEN`** to protect REST APIs
4. **Use HTTPS** behind nginx/Caddy/Traefik with Let's Encrypt
5. **Use `--reload` only in development** — start without it in production

## Architecture

```
┌──────────┐      ┌──────────────────────────────────────────┐
│ Browser  │─────▶│  FastAPI /podcast_generator/web/          │
│ (HTMX)   │      │                                          │
└──────────┘      │  Web UI: /, /settings, /fetch-articles   │
                  │  Auth:   /auth/google, /auth/callback     │
                  │  REST:   /api/v1/generate, /episodes      │
                  │  Files:  /download/{folder}/{file}        │
                  │  Feed:   /rss                             │
                  │  IMAP:   /fetch-more-emails, /imap-folders│
                  │                                          │
                  │  Background task → PodcastGenerator       │
                  │  (builder.py)                             │
                  └──────────────────┬───────────────────────┘
                                     │
                            ┌────────▼────────┐
                            │   podcast.db     │
                            │   (SQLite)       │
                            └─────────────────┘
```

## API Status Codes

| Code | Meaning |
|---|---|
| 200 | OK |
| 202 | Generation started (job_id returned) |
| 302 | Redirect (not authenticated → `/login`) |
| 303 | Redirect post-login / post-logout |
| 400 | Missing or invalid input |
| 401 | Invalid token/password |
| 404 | Episode/file not found |

## Technical Notes

- Podcast generation occurs in the **background** via `asyncio.create_task`
- Jobs are in **memory** (dict) — a server restart clears ongoing jobs
- Emails via IMAP support **Gmail X-GM-LABELS**
- 5 fallback strategies for email UID resolution
- RFC 2047 decoded email subjects
- Generated MP3 files are **persistent** in `output/`
- Episode history in **SQLite** (`podcast.db`) — persistent between restarts
- User sessions use **signed JWT** (cookie `session`, 7 days)
- OAuth callback manually exchanges the code with `httpx` (reliable even with `--reload`)
