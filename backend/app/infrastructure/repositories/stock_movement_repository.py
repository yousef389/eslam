from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import StockMovementRepository
from app.domain.entities import StockMovement
from app.domain.enums import StockMovementType
from app.infrastructure.models.inventory import StockMovementModel


class StockMovementRepositoryImpl(StockMovementRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: str) -> Optional[StockMovement]:
        stmt = select(StockMovementModel).where(StockMovementModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[StockMovement], int]:
        count_stmt = select(func.count()).select_from(StockMovementModel)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockMovementModel).order_by(StockMovementModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def create(self, entity: StockMovement) -> StockMovement:
        model = StockMovementModel(
            id=entity.id, movement_number=entity.movement_number, product_id=entity.product_id,
            warehouse_id=entity.warehouse_id, movement_type=entity.movement_type.value if hasattr(entity.movement_type, 'value') else entity.movement_type,
            quantity=entity.quantity, reference_id=entity.reference_id, notes=entity.notes,
            user_id=entity.user_id, created_at=entity.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: StockMovement) -> StockMovement:
        return entity

    async def delete(self, id: str) -> bool:
        stmt = select(StockMovementModel).where(StockMovementModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def get_by_product(self, product_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockMovement], int]:
        count_stmt = select(func.count()).select_from(StockMovementModel).where(StockMovementModel.product_id == product_id)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockMovementModel).where(StockMovementModel.product_id == product_id).order_by(StockMovementModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def get_by_warehouse(self, warehouse_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockMovement], int]:
        count_stmt = select(func.count()).select_from(StockMovementModel).where(StockMovementModel.warehouse_id == warehouse_id)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockMovementModel).where(StockMovementModel.warehouse_id == warehouse_id).order_by(StockMovementModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def get_by_type(self, movement_type: StockMovementType, page: int = 1, per_page: int = 20) -> Tuple[List[StockMovement], int]:
        mt = movement_type.value if hasattr(movement_type, 'value') else movement_type
        count_stmt = select(func.count()).select_from(StockMovementModel).where(StockMovementModel.movement_type == mt)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(StockMovementModel).where(StockMovementModel.movement_type == mt).order_by(StockMovementModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    def _to_entity(self, m: StockMovementModel) -> StockMovement:
        return StockMovement(
            id=m.id, movement_number=m.movement_number, product_id=m.product_id,
            warehouse_id=m.warehouse_id, movement_type=StockMovementType(m.movement_type),
            quantity=m.quantity, reference_id=m.reference_id, notes=m.notes or "",
            user_id=m.user_id, created_at=m.created_at,
        )
