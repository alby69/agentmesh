# Podcast Generator — Python Library

## Installation

```bash
pip install -r requirements.txt
# or, if published:
# pip install podcast-generator
```

Optional dependencies for LLM providers:

```bash
pip install openai              # OpenAI Provider
pip install anthropic           # Anthropic Provider
# Ollama works via HTTP (httpx, already in requirements.txt)
```

## Configuration

### With `.env` file

Create a `.env` in the working directory:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key
NEWSLETTER_URL=https://example.com
```

Then:

```python
from podcast_generator.config import Settings

cfg = Settings()  # Automatically reads from .env
cfg.validate()    # Verifies mandatory fields
```

### Without `.env` file

```python
cfg = Settings(
    llm_provider="openai",
    openai_api_key="sk-...",
    openai_model="gpt-4o",
    newsletter_url="https://newsletter.example.com",
)
```

### All Configuration Options

```python
cfg = Settings(
    # ── LLM ──
    llm_provider="gemini",       # gemini | openai | anthropic | ollama
    gemini_api_key="...",
    gemini_model="gemini-2.0-flash",
    openai_api_key="...",
    openai_model="gpt-4o-mini",
    anthropic_api_key="...",
    anthropic_model="claude-3-5-haiku-latest",
    ollama_base_url="http://localhost:11434",
    ollama_model="llama3",

    # ── TTS ──
    tts_provider="edge",         # edge | elevenlabs
    tts_voice="it-IT-GiuseppeNeural",
    elevenlabs_api_key="...",
    elevenlabs_voice="...",

    # ── Source ──
    source_name="My Newsletter",
    newsletter_url="https://newsletter.example.com",
    archive_url="https://newsletter.example.com/archive",

    # ── Scraping ──
    load_more_selector="button:has-text('Load More')",
    link_pattern="/p/",

    # ── Audio ──
    max_episode_minutes=60,
    output_dir=Path("./output"),
    use_web_search=False,
    intro_path=Path("./intro.mp3"),
    outro_path=Path("./outro.mp3"),
)
```

## Public API — `PodcastGenerator`

The main class. Accepts an optional configuration.

```python
from podcast_generator import PodcastGenerator, Settings

gen = PodcastGenerator()                          # Config from .env
gen = PodcastGenerator(Settings(...))             # Custom config
```

## v3.0 Evolution: Specialized Agents

In PodcastGen 3.0, you can directly use agents for more granular control and decentralized workflows.

### `ContentAgent`
Handles generation logic (fetch, translate, synthesis).
```python
from podcast_generator.agents.content_agent import ContentAgent
agent = ContentAgent(cfg)
episode = await agent.generate_episode_from_newsletter(newsletter)
```

### `NetworkAgent` (Nostr)
Manages identity and P2P publishing.
```python
from podcast_generator.agents.network_agent import NetworkAgent
agent = NetworkAgent(cfg, secret_key="...")
await agent.publish_podcast("Title", "IPFS_CID", metadata={})
```

### `StorageAgent` (IPFS)
Manages upload and retrieval via Content-Addressing.
```python
from podcast_generator.agents.storage_agent import StorageAgent
agent = StorageAgent(cfg)
cid = await agent.upload_file(path_to_audio)
```

### Fetching

#### `fetch_articles(url=None) -> list[ArticleSummary]`

Extracts the list of articles from a newsletter archive page.

```python
articles = await gen.fetch_articles("https://newsletter.example.com")
for a in articles:
    print(f"{a.text} — {a.href}")
# Output:
# AI Framework XYZ 5.0 — https://.../p/ai-framework-xyz
# OpenAI GPT-5 — https://.../p/openai-gpt5
```

### Episode Generation

#### `fetch_and_build_latest() -> Episode`

Downloads the latest newsletter and generates the episode.

```python
ep = await gen.fetch_and_build_latest()
print(f"Audio: {ep.audio_path}")
print(f"Duration: {ep.duration_minutes} min")
print(f"Script saved in: {ep.script_path}")
```

#### `build_daily(newsletter: Newsletter) -> Episode`

Generates an episode from an already obtained Newsletter object.

```python
nl = Newsletter(title="...", url="...", date=datetime.now(), content="...")
ep = await gen.build_daily(nl)
```

#### `build_from_urls(urls: list[str]) -> Episode`

Accepts a list of article URLs. If one URL → daily episode.
If multiple → weekly episode (compilation).

```python
ep = await gen.build_from_urls([
    "https://example.com/p/article-1",
    "https://example.com/p/article-2",
])
```

#### `fetch_and_build_weekly(days=7) -> Episode`

Downloads the last N newsletters and merges them into a weekly episode.

```python
ep = await gen.fetch_and_build_weekly(days=14)  # last 14 days
```

#### `build_weekly(newsletters: list[Newsletter]) -> Episode`

```python
newsletters = await gen.fetch_newsletters(...)
ep = await gen.build_weekly(newsletters)
```

#### `process_backlog(limit=None) -> dict`

Downloads **all** unprocessed newsletters and generates episodes.

```python
result = await gen.process_backlog(limit=10)
print(f"Generated: {len(result['daily'])} daily, {len(result['weekly'])} weekly")
```

## Multi-LLM: Configuration per provider

### Gemini (default, free)

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash       # or gemini-1.5-flash, gemini-2.5-pro
```

```python
cfg = Settings(llm_provider="gemini", gemini_api_key="AIza...")
```

### OpenAI

```bash
pip install openai
```

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini            # or gpt-4o, gpt-4-turbo, gpt-3.5-turbo
```

### Anthropic

```bash
pip install anthropic
```

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku-latest   # or claude-3-opus, claude-3-sonnet
```

### Ollama (local)

```bash
# Install Ollama: https://ollama.com
ollama pull llama3
```

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

No API key necessary, everything is local.

## TTS: Configuration per provider

### Edge-TTS (default, free)

No API key. Available Italian voices:

```env
TTS_PROVIDER=edge
TTS_VOICE=it-IT-GiuseppeNeural    # Male (default)
# TTS_VOICE=it-IT-ElsaNeural      # Female
# TTS_VOICE=it-IT-DiegoNeural     # Male, young
# TTS_VOICE=it-IT-IsabellaNeural  # Female
```

### ElevenLabs

```bash
# Requires API key (paid)
ELEVENLABS_API_KEY=your-key
ELEVENLABS_VOICE=your-voice-id    # From ElevenLabs dashboard
TTS_VOICE=it-IT-GiuseppeNeural   # Fallback if ElevenLabs voice not found
```

## Error Handling

```python
from podcast_generator.exceptions import (
    PodcastGeneratorError,
    ConfigError,
    FetchError,
    TranslationError,
    TTSError,
    AudioError,
    TrackerError,
    AuthError,
    NotFoundError,
)

try:
    episode = await gen.fetch_and_build_latest()
except FetchError as e:
    print(f"Scraping error: {e}")
except TranslationError as e:
    print(f"LLM error: {e}")
except TTSError as e:
    print(f"TTS error: {e}")
except ConfigError as e:
    print(f"Missing configuration: {e}")
```

## Models

### `Newsletter`

```python
from podcast_generator import Newsletter

nl = Newsletter(
    title="AI News",                          # str
    url="https://.../p/article",              # str
    date=datetime.now(),                      # datetime
    content="Article content...",             # str
)
```

### `Episode`

```python
ep = Episode(
    audio_path=Path("./output/daily/...mp3"), # Path
    script_path=Path("./output/daily/...txt"),# Path
    script="Hello everyone...",              # str
    date_str="2026-05-27",                    # str
    title="AI News",                          # str
    url="https://...",                        # str
    duration_minutes=15.3,                    # float | None
)
```

### `ArticleSummary`

```python
summary = ArticleSummary(
    href="https://.../p/article",             # str
    text="AI Framework XYZ 5.0",              # str (title)
    description="New framework...",           # str (short description)
)
```

### `GenerationJob`

Used internally by the web app to track asynchronous generation status.

```python
job = GenerationJob(
    job_id="uuid",                            # str
    status=JobStatus.PROCESSING,              # JobStatus enum
    download_url="/download/daily/...mp3",    # str | None
    title="AI News",                          # str | None
    filename="...mp3",                        # str | None
    error=None,                               # str | None
)
```

## Complete Examples

### Automatic Daily Episode

```python
import asyncio
from podcast_generator import PodcastGenerator

async def main():
    gen = PodcastGenerator()
    ep = await gen.fetch_and_build_latest()
    print(f"Episode created: {ep.audio_path} ({ep.duration_minutes:.1f} min)")

asyncio.run(main())
```

### Article Selection and Generation

```python
import asyncio
from podcast_generator import PodcastGenerator

async def main():
    gen = PodcastGenerator()

    # 1. Load article list
    articles = await gen.fetch_articles("https://newsletter.example.com")

    # 2. Take the first 3
    urls = [a.href for a in articles[:3]]

    # 3. Generate (if 1 → daily, if >1 → weekly compilation)
    ep = await gen.build_from_urls(urls)
    print(f"Podcast ready: {ep.audio_path}")

asyncio.run(main())
```

### With OpenAI

```python
import asyncio
from podcast_generator import PodcastGenerator, Settings

async def main():
    cfg = Settings(
        llm_provider="openai",
        openai_api_key="sk-...",
        openai_model="gpt-4o",
        newsletter_url="https://newsletter.example.com",
    )
    gen = PodcastGenerator(cfg)
    ep = await gen.fetch_and_build_latest()
    print(f"Done! {ep.audio_path}")

asyncio.run(main())
```

### With Ollama (local)

```python
cfg = Settings(
    llm_provider="ollama",
    ollama_base_url="http://localhost:11434",
    ollama_model="llama3",
    newsletter_url="https://newsletter.example.com",
)
```

## Integration in Other Projects

### As a Subprocess

```python
import subprocess, json

result = subprocess.run(
    ["python", "main.py", "daily"],
    cwd="/path/to/podcast-generator",
    capture_output=True, text=True,
)
print(result.stdout)
```

### As an Imported Module

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("/path/to/podcast-generator")))

from podcast_generator import PodcastGenerator

gen = PodcastGenerator()
```

### As an Installed Package

```bash
cd podcast-generator
pip install -e .                # Editable installation
# Or, after publishing to PyPI:
# pip install podcast-generator
```

Then from any project:

```python
from podcast_generator import PodcastGenerator
```
