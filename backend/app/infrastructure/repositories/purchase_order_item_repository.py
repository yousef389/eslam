from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import PurchaseOrderItem
from app.domain.repositories import PurchaseOrderItemRepository
from app.domain.value_objects import Money
from app.infrastructure.models.purchase_orders import PurchaseOrderItemModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: PurchaseOrderItemModel) -> PurchaseOrderItem:
    return PurchaseOrderItem(
        id=model.id,
        order_id=model.order_id,
        product_id=model.product_id,
        quantity=model.quantity,
        unit_price=Money(amount=Decimal(str(model.unit_price))),
        discount=Money(amount=Decimal(str(model.discount))),
        total=Money(amount=Decimal(str(model.total))),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: PurchaseOrderItem) -> PurchaseOrderItemModel:
    return PurchaseOrderItemModel(
        id=entity.id,
        order_id=entity.order_id,
        product_id=entity.product_id,
        quantity=entity.quantity,
        unit_price=float(entity.unit_price.amount),
        discount=float(entity.discount.amount),
        total=float(entity.total.amount),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class PurchaseOrderItemRepositoryImpl(PurchaseOrderItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, PurchaseOrderItemModel)

    async def get_by_id(self, id: str) -> Optional[PurchaseOrderItem]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[PurchaseOrderItem], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: PurchaseOrderItem) -> PurchaseOrderItem:
        model = _entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _model_to_entity(model)

    async def update(self, entity: PurchaseOrderItem) -> PurchaseOrderItem:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.order_id = entity.order_id
            model.product_id = entity.product_id
            model.quantity = entity.quantity
            model.unit_price = float(entity.unit_price.amount)
            model.discount = float(entity.discount.amount)
            model.total = float(entity.total.amount)
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        item = await self._repo.get_by_id(id)
        if item:
            await self._session.delete(item)
            await self._session.flush()
            return True
        return False

    async def get_by_order(
        self, order_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseOrderItem], int]:
        count_stmt = (
            select(func.count())
            .select_from(PurchaseOrderItemModel)
            .where(PurchaseOrderItemModel.order_id == order_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(PurchaseOrderItemModel)
            .where(PurchaseOrderItemModel.order_id == order_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
