from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import SaleOrder
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.repositories import SaleOrderRepository
from app.domain.value_objects import Money
from app.infrastructure.models.customers import CustomerModel
from app.infrastructure.models.sale_orders import SaleOrderModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: SaleOrderModel) -> SaleOrder:
    return SaleOrder(
        id=model.id,
        order_number=model.order_number,
        customer_id=model.customer_id,
        user_id=model.user_id,
        status=OrderStatus(model.status),
        subtotal=Money(amount=Decimal(str(model.subtotal))),
        discount=Money(amount=Decimal(str(model.discount))),
        tax_amount=Money(amount=Decimal(str(model.tax_amount))),
        total=Money(amount=Decimal(str(model.total))),
        payment_method=PaymentMethod(model.payment_method) if model.payment_method else None,
        notes=model.notes or "",
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: SaleOrder) -> SaleOrderModel:
    return SaleOrderModel(
        id=entity.id,
        order_number=entity.order_number,
        customer_id=entity.customer_id,
        user_id=entity.user_id,
        status=entity.status.value,
        subtotal=float(entity.subtotal.amount),
        discount=float(entity.discount.amount),
        tax_amount=float(entity.tax_amount.amount),
        total=float(entity.total.amount),
        payment_method=entity.payment_method.value if entity.payment_method else None,
        notes=entity.notes or None,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SaleOrderRepositoryImpl(SaleOrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, SaleOrderModel)

    async def get_by_id(self, id: str) -> Optional[SaleOrder]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[SaleOrder], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[SaleOrder], int]:
        pattern = f"%{query}%"
        base_filter = (
            SaleOrderModel.order_number.ilike(pattern)
            | SaleOrderModel.customer_id.in_(
                select(CustomerModel.id).where(CustomerModel.name.ilike(pattern))
            )
        )

        count_stmt = select(func.count()).select_from(SaleOrderModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SaleOrderModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: SaleOrder) -> SaleOrder:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: SaleOrder) -> SaleOrder:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.order_number = entity.order_number
            model.customer_id = entity.customer_id
            model.user_id = entity.user_id
            model.status = entity.status.value
            model.subtotal = float(entity.subtotal.amount)
            model.discount = float(entity.discount.amount)
            model.tax_amount = float(entity.tax_amount.amount)
            model.total = float(entity.total.amount)
            model.payment_method = entity.payment_method.value if entity.payment_method else None
            model.notes = entity.notes or None
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_order_number(self, order_number: str) -> Optional[SaleOrder]:
        stmt = select(SaleOrderModel).where(SaleOrderModel.order_number == order_number)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None

    async def get_by_customer(
        self, customer_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleOrder], int]:
        count_stmt = (
            select(func.count())
            .select_from(SaleOrderModel)
            .where(SaleOrderModel.customer_id == customer_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SaleOrderModel)
            .where(SaleOrderModel.customer_id == customer_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleOrder], int]:
        base_filter = SaleOrderModel.created_at.between(start_date, end_date)

        count_stmt = select(func.count()).select_from(SaleOrderModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SaleOrderModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_daily_sales(self, date: datetime) -> Decimal:
        from datetime import timedelta
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        stmt = select(func.coalesce(func.sum(SaleOrderModel.total), 0)).where(
            SaleOrderModel.created_at.between(start, end),
            SaleOrderModel.status != OrderStatus.CANCELLED.value,
        )
        result = await self._session.execute(stmt)
        total = result.scalar()
        return Decimal(str(total))

    async def get_recent(self, limit: int = 10) -> Tuple[List[SaleOrder], int]:
        stmt = (
            select(SaleOrderModel)
            .order_by(SaleOrderModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], len(models)
