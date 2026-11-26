import time
import threading
from typing import Any, Dict, List, Optional, Set
from app.core.logging import logger


class CacheEntry:
    __slots__ = ("value", "expires_at", "tags", "last_accessed")

    def __init__(self, value: Any, ttl_seconds: float, tags: Optional[List[str]] = None):
        self.value = value
        now = time.time()
        self.expires_at = now + ttl_seconds if ttl_seconds > 0 else float("inf")
        self.tags = set(tags) if tags else set()
        self.last_accessed = time.perf_counter()

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class InMemoryCacheManager:
    """
    High-performance thread-safe in-memory cache with:
    - Time-to-Live (TTL) expiration
    - Tag-based namespace invalidation (e.g. invalidate all 'risk' or 'forecast:SKU-123' keys)
    - Least Recently Used (LRU) max capacity eviction
    """

    def __init__(self, max_entries: int = 5000):
        self._max_entries = max_entries
        self._cache: Dict[str, CacheEntry] = {}
        self._tag_to_keys: Dict[str, Set[str]] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                self._remove_key(key)
                self._misses += 1
                return None

            entry.last_accessed = time.perf_counter()
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: float = 60.0, tags: Optional[List[str]] = None):
        with self._lock:
            # Check capacity and evict LRU if needed
            if len(self._cache) >= self._max_entries and key not in self._cache:
                self._evict_lru()

            # Remove old key association with tags if updating existing key
            if key in self._cache:
                self._remove_key(key)

            entry = CacheEntry(value, ttl_seconds, tags)
            self._cache[key] = entry

            if tags:
                for tag in tags:
                    if tag not in self._tag_to_keys:
                        self._tag_to_keys[tag] = set()
                    self._tag_to_keys[tag].add(key)

    def invalidate_tag(self, tag: str) -> int:
        """
        Invalidates and removes all cache entries associated with a specific tag.
        """
        with self._lock:
            keys = self._tag_to_keys.get(tag, set()).copy()
            for key in keys:
                self._remove_key(key)
            self._tag_to_keys.pop(tag, None)
            if keys:
                logger.debug(f"Cache invalidated tag '{tag}': {len(keys)} keys purged.")
            return len(keys)

    def invalidate_key(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                self._remove_key(key)
                return True
            return False

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._tag_to_keys.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_requests = self._hits + self._misses
            hit_ratio = (self._hits / total_requests) if total_requests > 0 else 0.0
            return {
                "total_entries": len(self._cache),
                "total_tags": len(self._tag_to_keys),
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio": round(hit_ratio, 4),
            }

    def _remove_key(self, key: str):
        entry = self._cache.pop(key, None)
        if entry:
            for tag in entry.tags:
                if tag in self._tag_to_keys and key in self._tag_to_keys[tag]:
                    self._tag_to_keys[tag].remove(key)
                    if not self._tag_to_keys[tag]:
                        del self._tag_to_keys[tag]

    def _evict_lru(self):
        if not self._cache:
            return
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
        self._remove_key(oldest_key)


cache_manager = InMemoryCacheManager()
