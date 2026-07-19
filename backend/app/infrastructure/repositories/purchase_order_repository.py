from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import PurchaseOrder
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.repositories import PurchaseOrderRepository
from app.domain.value_objects import Money
from app.infrastructure.models.purchase_orders import PurchaseOrderModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: PurchaseOrderModel) -> PurchaseOrder:
    return PurchaseOrder(
        id=model.id,
        order_number=model.order_number,
        supplier_id=model.supplier_id,
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


def _entity_to_model(entity: PurchaseOrder) -> PurchaseOrderModel:
    return PurchaseOrderModel(
        id=entity.id,
        order_number=entity.order_number,
        supplier_id=entity.supplier_id,
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


class PurchaseOrderRepositoryImpl(PurchaseOrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, PurchaseOrderModel)

    async def get_by_id(self, id: str) -> Optional[PurchaseOrder]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[PurchaseOrder], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: PurchaseOrder) -> PurchaseOrder:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: PurchaseOrder) -> PurchaseOrder:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.order_number = entity.order_number
            model.supplier_id = entity.supplier_id
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

    async def get_by_order_number(self, order_number: str) -> Optional[PurchaseOrder]:
        stmt = select(PurchaseOrderModel).where(PurchaseOrderModel.order_number == order_number)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None

    async def get_by_supplier(
        self, supplier_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseOrder], int]:
        count_stmt = (
            select(func.count())
            .select_from(PurchaseOrderModel)
            .where(PurchaseOrderModel.supplier_id == supplier_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(PurchaseOrderModel)
            .where(PurchaseOrderModel.supplier_id == supplier_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseOrder], int]:
        base_filter = PurchaseOrderModel.created_at.between(start_date, end_date)

        count_stmt = select(func.count()).select_from(PurchaseOrderModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(PurchaseOrderModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
