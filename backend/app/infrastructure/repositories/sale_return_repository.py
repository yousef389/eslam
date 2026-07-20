from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import SaleReturn
from app.domain.repositories import SaleReturnRepository
from app.domain.value_objects import Money
from app.infrastructure.models.sale_returns import SaleReturnModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: SaleReturnModel) -> SaleReturn:
    return SaleReturn(
        id=model.id,
        return_number=model.return_number,
        order_id=model.order_id,
        customer_id=model.customer_id,
        user_id=model.user_id,
        status=model.status,
        subtotal=Money(amount=Decimal(str(model.subtotal))),
        tax_amount=Money(amount=Decimal(str(model.tax_amount))),
        total=Money(amount=Decimal(str(model.total))),
        reason=model.reason or "",
        notes=model.notes or "",
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: SaleReturn) -> SaleReturnModel:
    return SaleReturnModel(
        id=entity.id,
        return_number=entity.return_number,
        order_id=entity.order_id,
        customer_id=entity.customer_id,
        user_id=entity.user_id,
        status=entity.status,
        subtotal=float(entity.subtotal.amount),
        tax_amount=float(entity.tax_amount.amount),
        total=float(entity.total.amount),
        reason=entity.reason or None,
        notes=entity.notes or None,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SaleReturnRepositoryImpl(SaleReturnRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, SaleReturnModel)

    async def get_by_id(self, id: str) -> Optional[SaleReturn]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[SaleReturn], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: SaleReturn) -> SaleReturn:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: SaleReturn) -> SaleReturn:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.status = entity.status
            model.subtotal = float(entity.subtotal.amount)
            model.tax_amount = float(entity.tax_amount.amount)
            model.total = float(entity.total.amount)
            model.reason = entity.reason or None
            model.notes = entity.notes or None
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_return_number(self, return_number: str) -> Optional[SaleReturn]:
        stmt = select(SaleReturnModel).where(SaleReturnModel.return_number == return_number)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None

    async def get_by_customer(
        self, customer_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleReturn], int]:
        count_stmt = select(func.count()).select_from(SaleReturnModel).where(
            SaleReturnModel.customer_id == customer_id
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SaleReturnModel)
            .where(SaleReturnModel.customer_id == customer_id)
            .order_by(SaleReturnModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
