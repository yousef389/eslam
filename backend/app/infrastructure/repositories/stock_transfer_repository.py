from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import StockTransferRepository
from app.domain.entities import StockTransfer
from app.infrastructure.models.inventory import StockTransferModel


class StockTransferRepositoryImpl(StockTransferRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: str) -> Optional[StockTransfer]:
        stmt = select(StockTransferModel).where(StockTransferModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[StockTransfer], int]:
        count_stmt = select(func.count()).select_from(StockTransferModel)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockTransferModel).order_by(StockTransferModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def create(self, entity: StockTransfer) -> StockTransfer:
        model = StockTransferModel(
            id=entity.id, transfer_number=entity.transfer_number, product_id=entity.product_id,
            from_warehouse_id=entity.from_warehouse_id, to_warehouse_id=entity.to_warehouse_id,
            quantity=entity.quantity, status=entity.status, notes=entity.notes,
            user_id=entity.user_id, created_at=entity.created_at, updated_at=entity.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: StockTransfer) -> StockTransfer:
        stmt = select(StockTransferModel).where(StockTransferModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            model.status = entity.status
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
        return self._to_entity(model) if model else entity

    async def delete(self, id: str) -> bool:
        stmt = select(StockTransferModel).where(StockTransferModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def get_by_product(self, product_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockTransfer], int]:
        count_stmt = select(func.count()).select_from(StockTransferModel).where(StockTransferModel.product_id == product_id)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockTransferModel).where(StockTransferModel.product_id == product_id).order_by(StockTransferModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def get_by_from_warehouse(self, warehouse_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockTransfer], int]:
        count_stmt = select(func.count()).select_from(StockTransferModel).where(StockTransferModel.from_warehouse_id == warehouse_id)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockTransferModel).where(StockTransferModel.from_warehouse_id == warehouse_id).order_by(StockTransferModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def get_by_to_warehouse(self, warehouse_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockTransfer], int]:
        count_stmt = select(func.count()).select_from(StockTransferModel).where(StockTransferModel.to_warehouse_id == warehouse_id)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockTransferModel).where(StockTransferModel.to_warehouse_id == warehouse_id).order_by(StockTransferModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    def _to_entity(self, m: StockTransferModel) -> StockTransfer:
        return StockTransfer(
            id=m.id, transfer_number=m.transfer_number, product_id=m.product_id,
            from_warehouse_id=m.from_warehouse_id, to_warehouse_id=m.to_warehouse_id,
            quantity=m.quantity, status=m.status, notes=m.notes or "",
            user_id=m.user_id, created_at=m.created_at, updated_at=m.updated_at,
        )
