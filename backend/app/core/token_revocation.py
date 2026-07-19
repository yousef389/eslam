from __future__ import annotations

from datetime import datetime, timezone


class TokenRevocationService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self._prefix = "token_revoked"
        self._all_prefix = "revoked_all"

    async def init(self):
        try:
            await self.redis.ping()
        except Exception:
            pass

    async def revoke_token(self, jti: str, expires_at: datetime):
        now = datetime.now(timezone.utc)
        ttl = int((expires_at - now).total_seconds())
        if ttl <= 0:
            return

        key = f"{self._prefix}:{jti}"
        await self.redis.set(key, "1", ex=ttl)

    async def is_token_revoked(self, jti: str) -> bool:
        key = f"{self._prefix}:{jti}"
        return bool(await self.redis.exists(key))

    async def revoke_all_user_tokens(self, user_id: str):
        key = f"{self._all_prefix}:{user_id}"
        await self.redis.set(key, "1", ex=7 * 24 * 3600)

    async def is_all_revoked(self, user_id: str) -> bool:
        key = f"{self._all_prefix}:{user_id}"
        return bool(await self.redis.exists(key))

    async def close(self):
        try:
            await self.redis.aclose()
        except Exception:
            pass
