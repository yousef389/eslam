import json

import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class CacheService:
    def __init__(self, client: redis.Redis | None = None) -> None:
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
        cursor = 0
        while True:
            cursor, keys = await self._client.scan(cursor, match=pattern, count=100)
            if keys:
                await self._client.delete(*keys)
            if cursor == 0:
                break

    async def incr(self, key: str) -> int:
        return await self._client.incr(key)

    async def expire(self, key: str, ttl: int) -> None:
        await self._client.expire(key, ttl)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))
