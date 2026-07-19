from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import CustomerDebt
from app.domain.enums import DebtStatus
from app.domain.repositories import CustomerDebtRepository
from app.domain.value_objects import Money
from app.infrastructure.models.debts import CustomerDebtModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: CustomerDebtModel) -> CustomerDebt:
    return CustomerDebt(
        id=model.id,
        customer_id=model.customer_id,
        amount=Money(amount=Decimal(str(model.amount))),
        paid_amount=Money(amount=Decimal(str(model.paid_amount))),
        remaining=Money(amount=Decimal(str(model.remaining))),
        status=DebtStatus(model.status),
        description=model.description or "",
        due_date=model.due_date,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: CustomerDebt) -> CustomerDebtModel:
    return CustomerDebtModel(
        id=entity.id,
        customer_id=entity.customer_id,
        amount=float(entity.amount.amount),
        paid_amount=float(entity.paid_amount.amount),
        remaining=float(entity.remaining.amount),
        status=entity.status.value,
        description=entity.description or None,
        due_date=entity.due_date,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class CustomerDebtRepositoryImpl(CustomerDebtRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, CustomerDebtModel)

    async def get_by_id(self, id: str) -> Optional[CustomerDebt]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[CustomerDebt], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: CustomerDebt) -> CustomerDebt:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: CustomerDebt) -> CustomerDebt:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.customer_id = entity.customer_id
            model.amount = float(entity.amount.amount)
            model.paid_amount = float(entity.paid_amount.amount)
            model.remaining = float(entity.remaining.amount)
            model.status = entity.status.value
            model.description = entity.description or None
            model.due_date = entity.due_date
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_customer(
        self, customer_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CustomerDebt], int]:
        count_stmt = (
            select(func.count())
            .select_from(CustomerDebtModel)
            .where(CustomerDebtModel.customer_id == customer_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(CustomerDebtModel)
            .where(CustomerDebtModel.customer_id == customer_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_overdue(self, page: int = 1, per_page: int = 20) -> Tuple[List[CustomerDebt], int]:
        base_filter = CustomerDebtModel.status == DebtStatus.OVERDUE.value

        count_stmt = select(func.count()).select_from(CustomerDebtModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(CustomerDebtModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_pending(self, page: int = 1, per_page: int = 20) -> Tuple[List[CustomerDebt], int]:
        base_filter = CustomerDebtModel.status.in_([
            DebtStatus.PENDING.value,
            DebtStatus.PARTIAL.value,
        ])

        count_stmt = select(func.count()).select_from(CustomerDebtModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(CustomerDebtModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
