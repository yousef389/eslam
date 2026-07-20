from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import SaleReturnItem
from app.domain.repositories import SaleReturnItemRepository
from app.domain.value_objects import Money
from app.infrastructure.models.sale_returns import SaleReturnItemModel

from .base import BaseRepositoryImpl
from decimal import Decimal


def _model_to_entity(model: SaleReturnItemModel) -> SaleReturnItem:
    return SaleReturnItem(
        id=model.id,
        return_id=model.return_id,
        product_id=model.product_id,
        quantity=model.quantity,
        unit_price=Money(amount=Decimal(str(model.unit_price))),
        total=Money(amount=Decimal(str(model.total))),
        created_at=model.created_at,
    )


def _entity_to_model(entity: SaleReturnItem) -> SaleReturnItemModel:
    return SaleReturnItemModel(
        id=entity.id,
        return_id=entity.return_id,
        product_id=entity.product_id,
        quantity=entity.quantity,
        unit_price=float(entity.unit_price.amount),
        total=float(entity.total.amount),
        created_at=entity.created_at,
    )


class SaleReturnItemRepositoryImpl(SaleReturnItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, SaleReturnItemModel)

    async def get_by_id(self, id: str) -> Optional[SaleReturnItem]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[SaleReturnItem], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: SaleReturnItem) -> SaleReturnItem:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: SaleReturnItem) -> SaleReturnItem:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.quantity = entity.quantity
            model.unit_price = float(entity.unit_price.amount)
            model.total = float(entity.total.amount)
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_return(
        self, return_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleReturnItem], int]:
        count_stmt = select(func.count()).select_from(SaleReturnItemModel).where(
            SaleReturnItemModel.return_id == return_id
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SaleReturnItemModel)
            .where(SaleReturnItemModel.return_id == return_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
