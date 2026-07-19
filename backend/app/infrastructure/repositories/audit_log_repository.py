import json
from datetime import datetime
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AuditLog
from app.domain.repositories import AuditLogRepository
from app.infrastructure.models.audit_logs import AuditLogModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: AuditLogModel) -> AuditLog:
    details = {}
    if model.details:
        try:
            details = json.loads(model.details)
        except (json.JSONDecodeError, TypeError):
            details = {}

    return AuditLog(
        id=model.id,
        user_id=model.user_id or "",
        action=model.action,
        resource_type=model.resource_type,
        resource_id=model.resource_id or "",
        details=details,
        ip_address=model.ip_address or "",
        created_at=model.created_at,
    )


def _entity_to_model(entity: AuditLog) -> AuditLogModel:
    return AuditLogModel(
        id=entity.id,
        user_id=entity.user_id or None,
        action=entity.action,
        resource_type=entity.resource_type,
        resource_id=entity.resource_id or None,
        details=json.dumps(entity.details) if entity.details else None,
        ip_address=entity.ip_address or None,
        created_at=entity.created_at,
    )


class AuditLogRepositoryImpl(AuditLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, AuditLogModel)

    async def get_by_id(self, id: str) -> Optional[AuditLog]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[AuditLog], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: AuditLog) -> AuditLog:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: AuditLog) -> AuditLog:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.user_id = entity.user_id or None
            model.action = entity.action
            model.resource_type = entity.resource_type
            model.resource_id = entity.resource_id or None
            model.details = json.dumps(entity.details) if entity.details else None
            model.ip_address = entity.ip_address or None
            model.created_at = entity.created_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_user(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[AuditLog], int]:
        count_stmt = (
            select(func.count())
            .select_from(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
            .order_by(AuditLogModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_resource(
        self, resource_type: str, resource_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[AuditLog], int]:
        base_filter = AuditLogModel.resource_type == resource_type
        if resource_id:
            base_filter = base_filter & (AuditLogModel.resource_id == resource_id)

        count_stmt = select(func.count()).select_from(AuditLogModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(AuditLogModel)
            .where(base_filter)
            .order_by(AuditLogModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[AuditLog], int]:
        base_filter = AuditLogModel.created_at.between(start_date, end_date)

        count_stmt = select(func.count()).select_from(AuditLogModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(AuditLogModel)
            .where(base_filter)
            .order_by(AuditLogModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
