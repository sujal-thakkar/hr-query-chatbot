import json
import time
import logging
from typing import Any, Optional

from config import REDIS_URL, CACHE_BACKEND, QUERY_CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)

try:
    import redis  # type: ignore
    _REDIS_AVAILABLE = True
except Exception:
    _REDIS_AVAILABLE = False


class BaseCache:
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        raise NotImplementedError

    def size(self) -> Optional[int]:
        return None


class MemoryCache(BaseCache):
    def __init__(self, prefix: str = "", capacity: int = 1000, default_ttl: int = QUERY_CACHE_TTL_SECONDS):
        self.prefix = prefix
        self.capacity = capacity
        self.default_ttl = default_ttl
        # key -> (ts, ttl, value)
        self._store: dict[str, tuple[float, int, Any]] = {}

    def _pk(self, key: str) -> str:
        return f"{self.prefix}:{key}" if self.prefix else key

    def get(self, key: str) -> Optional[Any]:
        pk = self._pk(key)
        item = self._store.get(pk)
        if not item:
            return None
        ts, ttl, value = item
        if time.time() - ts > ttl:
            self._store.pop(pk, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        pk = self._pk(key)
        if len(self._store) >= self.capacity:
            # simple FIFO eviction
            oldest_key = next(iter(self._store))
            self._store.pop(oldest_key, None)
        self._store[pk] = (time.time(), int(ttl_seconds or self.default_ttl), value)

    def size(self) -> Optional[int]:
        return len(self._store)


class RedisCache(BaseCache):
    def __init__(self, url: str, prefix: str = "", default_ttl: int = QUERY_CACHE_TTL_SECONDS):
        self.prefix = prefix
        self.default_ttl = default_ttl
        self._client = redis.Redis.from_url(url, decode_responses=True)
        # test connection quickly
        try:
            self._client.ping()
        except Exception as e:
            raise RuntimeError(f"Redis not reachable: {e}")

    def _pk(self, key: str) -> str:
        return f"{self.prefix}:{key}" if self.prefix else key

    def get(self, key: str) -> Optional[Any]:
        pk = self._pk(key)
        data = self._client.get(pk)
        if data is None:
            return None
        try:
            return json.loads(data)
        except Exception:
            return data

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        pk = self._pk(key)
        data = value
        if not isinstance(value, (str, int, float)):
            data = json.dumps(value)
        ttl = int(ttl_seconds or self.default_ttl)
        self._client.set(pk, data, ex=ttl)

    # size() is expensive on Redis; return None


def get_cache(prefix: str = "", default_ttl: int = QUERY_CACHE_TTL_SECONDS) -> BaseCache:
    backend = (CACHE_BACKEND or "auto").lower()
    if backend == "memory":
        logger.info("Using MemoryCache for prefix=%s", prefix)
        return MemoryCache(prefix=prefix, default_ttl=default_ttl)

    if backend in ("auto", "redis") and REDIS_URL and _REDIS_AVAILABLE:
        try:
            logger.info("Attempting RedisCache for prefix=%s", prefix)
            return RedisCache(url=REDIS_URL, prefix=prefix, default_ttl=default_ttl)
        except Exception as e:
            logger.warning("Redis unavailable: %s; falling back to MemoryCache", e)

    logger.info("Using MemoryCache for prefix=%s", prefix)
    return MemoryCache(prefix=prefix, default_ttl=default_ttl)
