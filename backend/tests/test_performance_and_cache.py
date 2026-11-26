import time
import pytest
from app.core.cache import InMemoryCacheManager, cache_manager
from app.workers.forecast_jobs import ForecastJobRegistry
from app.services.rag.embedding import embedding_service


def test_cache_manager_basic_operations():
    cache = InMemoryCacheManager(max_entries=10)
    cache.set("key1", "value1", ttl_seconds=10.0, tags=["tagA"])
    
    assert cache.get("key1") == "value1"
    assert cache.get("non_existent") is None
    
    stats = cache.get_stats()
    assert stats["total_entries"] == 1
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_cache_manager_ttl_expiration():
    cache = InMemoryCacheManager(max_entries=10)
    cache.set("short_lived", "expired_val", ttl_seconds=0.05, tags=["tagA"])
    
    assert cache.get("short_lived") == "expired_val"
    time.sleep(0.06)
    assert cache.get("short_lived") is None


def test_cache_manager_tag_invalidation():
    cache = InMemoryCacheManager(max_entries=100)
    cache.set("item1", {"data": 1}, ttl_seconds=60.0, tags=["risk", "sku:1"])
    cache.set("item2", {"data": 2}, ttl_seconds=60.0, tags=["risk", "sku:2"])
    cache.set("item3", {"data": 3}, ttl_seconds=60.0, tags=["forecast", "sku:1"])
    
    assert cache.get("item1") is not None
    assert cache.get("item2") is not None
    assert cache.get("item3") is not None
    
    # Invalidate all risk tags
    purged = cache.invalidate_tag("risk")
    assert purged == 2
    assert cache.get("item1") is None
    assert cache.get("item2") is None
    assert cache.get("item3") is not None  # Forecast item preserved


def test_cache_manager_lru_eviction():
    cache = InMemoryCacheManager(max_entries=3)
    cache.set("k1", "v1", ttl_seconds=60.0)
    time.sleep(0.005)
    cache.set("k2", "v2", ttl_seconds=60.0)
    time.sleep(0.005)
    cache.set("k3", "v3", ttl_seconds=60.0)
    time.sleep(0.005)
    
    # Access k1 to make k1 newer than k2
    _ = cache.get("k1")
    time.sleep(0.005)
    
    # Adding k4 should evict oldest (k2)
    cache.set("k4", "v4", ttl_seconds=60.0)
    assert cache.get("k2") is None
    assert cache.get("k1") == "v1"
    assert cache.get("k3") == "v3"
    assert cache.get("k4") == "v4"


def test_job_registry_deduplication():
    registry = ForecastJobRegistry()
    job_id1, is_new1 = registry.register_job("SKU-TEST-1", "prophet", 30)
    assert is_new1 is True
    
    # Duplicate registration while still in-flight
    job_id2, is_new2 = registry.register_job("SKU-TEST-1", "prophet", 30)
    assert is_new2 is False
    assert job_id2 == job_id1
    
    # Complete job
    registry.set_running(job_id1)
    registry.set_completed(job_id1, {"mape": 5.2})
    
    job_data = registry.get_job(job_id1)
    assert job_data["status"] == "COMPLETED"
    assert job_data["metrics"]["mape"] == 5.2
    
    # Now that it's completed, new registration is allowed
    job_id3, is_new3 = registry.register_job("SKU-TEST-1", "prophet", 30)
    assert is_new3 is True
    assert job_id3 != job_id1


def test_embedding_query_lru_caching():
    query = "What is the lead time for Apex Microelectronics?"
    vec1 = embedding_service.embed_query(query)
    vec2 = embedding_service.embed_query(query)
    
    assert len(vec1) == embedding_service.DIMENSION
    assert vec1 == vec2
