from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.audit_logs import AuditLogModel


class AuditLogService:
    def __init__(self, db_session: AsyncSession, redis_client=None):
        self.db = db_session
        self.redis = redis_client

    async def log(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLogModel:
        audit_entry = AuditLogModel(
            id=str(uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(audit_entry)
        await self.db.flush()

        if self.redis:
            try:
                cache_key = f"audit:user:{user_id}:recent"
                entry = {
                    "id": audit_entry.id,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "created_at": audit_entry.created_at.isoformat(),
                }
                await self.redis.lpush(cache_key, json.dumps(entry))
                await self.redis.ltrim(cache_key, 0, 49)
                await self.redis.expire(cache_key, 3600)
            except Exception:
                pass

        return audit_entry

    async def get_user_activity(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        if self.redis:
            try:
                cache_key = f"audit:user:{user_id}:recent"
                cached = await self.redis.lrange(cache_key, 0, limit - 1)
                if cached:
                    return [json.loads(item) for item in cached]
            except Exception:
                pass

        stmt = (
            select(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
            .order_by(AuditLogModel.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [
            {
                "id": m.id,
                "action": m.action,
                "resource_type": m.resource_type,
                "resource_id": m.resource_id,
                "details": json.loads(m.details) if m.details else None,
                "ip_address": m.ip_address,
                "created_at": m.created_at.isoformat(),
            }
            for m in models
        ]

    async def get_resource_history(
        self, resource_type: str, resource_id: str
    ) -> list[dict[str, Any]]:
        stmt = (
            select(AuditLogModel)
            .where(
                AuditLogModel.resource_type == resource_type,
                AuditLogModel.resource_id == resource_id,
            )
            .order_by(AuditLogModel.created_at.desc())
            .limit(100)
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [
            {
                "id": m.id,
                "user_id": m.user_id,
                "action": m.action,
                "details": json.loads(m.details) if m.details else None,
                "ip_address": m.ip_address,
                "created_at": m.created_at.isoformat(),
            }
            for m in models
        ]
