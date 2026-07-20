from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import PurchaseReturnItem
from app.domain.repositories import PurchaseReturnItemRepository
from app.domain.value_objects import Money
from app.infrastructure.models.purchase_returns import PurchaseReturnItemModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: PurchaseReturnItemModel) -> PurchaseReturnItem:
    return PurchaseReturnItem(
        id=model.id,
        return_id=model.return_id,
        product_id=model.product_id,
        quantity=model.quantity,
        unit_price=Money(amount=Decimal(str(model.unit_price))),
        total=Money(amount=Decimal(str(model.total))),
        created_at=model.created_at,
    )


def _entity_to_model(entity: PurchaseReturnItem) -> PurchaseReturnItemModel:
    return PurchaseReturnItemModel(
        id=entity.id,
        return_id=entity.return_id,
        product_id=entity.product_id,
        quantity=entity.quantity,
        unit_price=float(entity.unit_price.amount),
        total=float(entity.total.amount),
        created_at=entity.created_at,
    )


class PurchaseReturnItemRepositoryImpl(PurchaseReturnItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, PurchaseReturnItemModel)

    async def get_by_id(self, id: str) -> Optional[PurchaseReturnItem]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[PurchaseReturnItem], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: PurchaseReturnItem) -> PurchaseReturnItem:
        model = _entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _model_to_entity(model)

    async def update(self, entity: PurchaseReturnItem) -> PurchaseReturnItem:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.return_id = entity.return_id
            model.product_id = entity.product_id
            model.quantity = entity.quantity
            model.unit_price = float(entity.unit_price.amount)
            model.total = float(entity.total.amount)
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        item = await self._repo.get_by_id(id)
        if item:
            await self._session.delete(item)
            await self._session.flush()
            return True
        return False

    async def get_by_return(
        self, return_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseReturnItem], int]:
        count_stmt = (
            select(func.count())
            .select_from(PurchaseReturnItemModel)
            .where(PurchaseReturnItemModel.return_id == return_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(PurchaseReturnItemModel)
            .where(PurchaseReturnItemModel.return_id == return_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
