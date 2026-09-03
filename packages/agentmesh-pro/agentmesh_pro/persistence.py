"""Persistence and caching layer for AgentMesh Pro (PostgreSQL + PGVector + Redis with offline fallbacks)."""

import json
import logging
from typing import Any, Dict, List, Optional
from agentmesh_pro.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with in-memory fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self._redis_client = None
        self._in_memory_cache: Dict[str, str] = {}
        self._connect()

    def _connect(self):
        try:
            import redis
            self._redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self._redis_client.ping()
            logger.info("Connected to Redis cache.")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}). Falling back to in-memory caching.")
            self._redis_client = None

    def get(self, key: str) -> Optional[str]:
        if self._redis_client:
            try:
                return self._redis_client.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        return self._in_memory_cache.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = 3600):
        if self._redis_client:
            try:
                self._redis_client.set(key, value, ex=ex)
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
        self._in_memory_cache[key] = value

    def delete(self, key: str):
        if self._redis_client:
            try:
                self._redis_client.delete(key)
                return
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")
        self._in_memory_cache.pop(key, None)


class MemoryStore:
    """PostgreSQL + PGVector memory store with in-memory fallback for long-term RAG memory."""

    def __init__(self):
        self._db_connected = False
        self._in_memory_db: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                dbname=settings.postgres_db,
                connect_timeout=2,
            )
            cursor = conn.cursor()
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255),
                    key VARCHAR(255),
                    content TEXT,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            conn.close()
            self._db_connected = True
            logger.info("Connected to PostgreSQL + PGVector.")
        except Exception as e:
            logger.warning(f"PostgreSQL/PGVector unavailable ({e}). Falling back to in-memory store.")
            self._db_connected = False

    def store_memory(
        self,
        session_id: str,
        key: str,
        content: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        metadata = metadata or {}
        if self._db_connected:
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=settings.postgres_host,
                    port=settings.postgres_port,
                    user=settings.postgres_user,
                    password=settings.postgres_password,
                    dbname=settings.postgres_db,
                )
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO agent_memory (session_id, key, content, metadata)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (session_id, key, content, json.dumps(metadata)),
                )
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.warning(f"Failed to store memory in PostgreSQL: {e}")

        # Fallback
        self._in_memory_db.append({
            "session_id": session_id,
            "key": key,
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
        })
        return True

    def search_memory(self, session_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if self._db_connected:
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=settings.postgres_host,
                    port=settings.postgres_port,
                    user=settings.postgres_user,
                    password=settings.postgres_password,
                    dbname=settings.postgres_db,
                )
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT key, content, metadata FROM agent_memory
                    WHERE session_id = %s OR content ILIKE %s
                    LIMIT %s;
                    """,
                    (session_id, f"%{query}%", limit),
                )
                rows = cursor.fetchall()
                conn.close()
                return [{"key": r[0], "content": r[1], "metadata": r[2]} for r in rows]
            except Exception as e:
                logger.warning(f"Failed to search memory in PostgreSQL: {e}")

        # In-memory search fallback
        results = []
        for item in self._in_memory_db:
            if item["session_id"] == session_id or query.lower() in item["content"].lower():
                results.append({"key": item["key"], "content": item["content"], "metadata": item["metadata"]})
                if len(results) >= limit:
                    break
        return results


cache_manager = CacheManager()
memory_store = MemoryStore()
