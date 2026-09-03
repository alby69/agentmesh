"""Tests for persistence and caching in AgentMesh Pro."""

from agentmesh_pro.persistence import CacheManager, MemoryStore


def test_cache_manager_fallback():
    cache = CacheManager(redis_url="redis://nonexistent:6379/0")
    cache.set("key1", "val1")
    assert cache.get("key1") == "val1"
    cache.delete("key1")
    assert cache.get("key1") is None


def test_memory_store_fallback():
    store = MemoryStore()
    stored = store.store_memory("sess_1", "k1", "Sample content for testing memory")
    assert stored is True
    results = store.search_memory("sess_1", "Sample")
    assert len(results) >= 1
    assert results[0]["key"] == "k1"
