from __future__ import annotations

import json
import logging
import time
from typing import Any

from app.core.config import settings

logger = logging.getLogger("app.cache")


class InMemoryClient:
    """Fallback in-memory store when Redis is unavailable."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if item is None:
            return None
        value, expiry = item
        if expiry and time.time() > expiry:
            del self._store[key]
            return None
        return value

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        expiry = time.time() + ex if ex else None
        self._store[key] = (value, expiry)

    async def incr(self, key: str) -> int:
        item = self._store.get(key)
        if item is None:
            self._store[key] = ("1", None)
            return 1
        value, expiry = item
        new_val = int(value) + 1
        self._store[key] = (str(new_val), expiry)
        return new_val

    async def expire(self, key: str, ttl: int) -> None:
        item = self._store.get(key)
        if item:
            value, _ = item
            self._store[key] = (value, time.time() + ttl)

    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self._store.pop(key, None)

    async def ttl(self, key: str) -> int:
        item = self._store.get(key)
        if item is None:
            return -2
        _, expiry = item
        if expiry is None:
            return -1
        remaining = int(expiry - time.time())
        return max(remaining, -1)

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        self._store.clear()


async def _create_redis_client():
    """Try to create a Redis client; return InMemoryClient on failure."""
    try:
        import redis.asyncio as redis

        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        logger.info("Redis connected: %s", settings.REDIS_URL)
        return client
    except Exception as e:
        logger.warning("Redis unavailable (%s), using in-memory fallback", e)
        return InMemoryClient()


class _LazyClient:
    """Proxy that lazily initializes the real client on first use."""

    def __init__(self):
        self._client = None
        self._initializing = False

    async def _ensure(self):
        if self._client is None and not self._initializing:
            self._initializing = True
            try:
                self._client = await _create_redis_client()
            finally:
                self._initializing = False
        return self._client

    async def get(self, key: str) -> Any | None:
        client = await self._ensure()
        return await client.get(key)

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        client = await self._ensure()
        await client.set(key, value, ex=ex)

    async def incr(self, key: str) -> int:
        client = await self._ensure()
        return await client.incr(key)

    async def expire(self, key: str, ttl: int) -> None:
        client = await self._ensure()
        await client.expire(key, ttl)

    async def exists(self, key: str) -> bool:
        client = await self._ensure()
        return await client.exists(key)

    async def delete(self, *keys: str) -> None:
        client = await self._ensure()
        await client.delete(*keys)

    async def ttl(self, key: str) -> int:
        client = await self._ensure()
        return await client.ttl(key)

    async def ping(self) -> bool:
        client = await self._ensure()
        return await client.ping()

    async def aclose(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


redis_client = _LazyClient()


class CacheService:
    def __init__(self, client=None) -> None:
        self._client = client or redis_client

    async def get(self, key: str) -> str | None:
        value = await self._client.get(key)
        if value is not None:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None

    async def set(self, key: str, value: str | dict | list, ttl: int = 300) -> None:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self._client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        client = await self._client._ensure()
        if hasattr(client, "scan"):
            cursor = 0
            while True:
                cursor, keys = await client.scan(cursor, match=pattern, count=100)
                if keys:
                    await client.delete(*keys)
                if cursor == 0:
                    break

    async def incr(self, key: str) -> int:
        return await self._client.incr(key)

    async def expire(self, key: str, ttl: int) -> None:
        await self._client.expire(key, ttl)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))
