from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import WarehouseStockRepository
from app.domain.entities import WarehouseStock
from app.infrastructure.models.inventory import WarehouseStockModel


class WarehouseStockRepositoryImpl(WarehouseStockRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: str) -> Optional[WarehouseStock]:
        stmt = select(WarehouseStockModel).where(WarehouseStockModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[WarehouseStock], int]:
        count_stmt = select(func.count()).select_from(WarehouseStockModel)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(WarehouseStockModel).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def create(self, entity: WarehouseStock) -> WarehouseStock:
        model = WarehouseStockModel(
            id=entity.id, warehouse_id=entity.warehouse_id, product_id=entity.product_id,
            quantity=entity.quantity, created_at=entity.created_at, updated_at=entity.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: WarehouseStock) -> WarehouseStock:
        stmt = select(WarehouseStockModel).where(WarehouseStockModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            model.quantity = entity.quantity
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
        return self._to_entity(model) if model else entity

    async def delete(self, id: str) -> bool:
        stmt = select(WarehouseStockModel).where(WarehouseStockModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def get_by_warehouse(self, warehouse_id: str) -> List[WarehouseStock]:
        stmt = select(WarehouseStockModel).where(WarehouseStockModel.warehouse_id == warehouse_id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_product(self, product_id: str) -> List[WarehouseStock]:
        stmt = select(WarehouseStockModel).where(WarehouseStockModel.product_id == product_id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_warehouse_and_product(self, warehouse_id: str, product_id: str) -> Optional[WarehouseStock]:
        stmt = select(WarehouseStockModel).where(
            WarehouseStockModel.warehouse_id == warehouse_id,
            WarehouseStockModel.product_id == product_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    def _to_entity(self, m: WarehouseStockModel) -> WarehouseStock:
        return WarehouseStock(
            id=m.id, warehouse_id=m.warehouse_id, product_id=m.product_id,
            quantity=m.quantity, created_at=m.created_at, updated_at=m.updated_at,
        )
