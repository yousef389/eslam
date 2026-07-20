from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import WarehouseRepository
from app.domain.entities import Warehouse
from app.infrastructure.models.inventory import WarehouseModel


class WarehouseRepositoryImpl(WarehouseRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: str) -> Optional[Warehouse]:
        stmt = select(WarehouseModel).where(WarehouseModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Warehouse], int]:
        count_stmt = select(func.count()).select_from(WarehouseModel)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(WarehouseModel).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def create(self, entity: Warehouse) -> Warehouse:
        model = WarehouseModel(
            id=entity.id, name=entity.name, location=entity.location,
            is_active=entity.is_active, created_at=entity.created_at, updated_at=entity.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: Warehouse) -> Warehouse:
        stmt = select(WarehouseModel).where(WarehouseModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            model.name = entity.name
            model.location = entity.location
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
        return self._to_entity(model) if model else entity

    async def delete(self, id: str) -> bool:
        stmt = select(WarehouseModel).where(WarehouseModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def get_by_name(self, name: str) -> Optional[Warehouse]:
        stmt = select(WarehouseModel).where(WarehouseModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    def _to_entity(self, m: WarehouseModel) -> Warehouse:
        return Warehouse(
            id=m.id, name=m.name, location=m.location or "",
            is_active=m.is_active, created_at=m.created_at, updated_at=m.updated_at,
        )
