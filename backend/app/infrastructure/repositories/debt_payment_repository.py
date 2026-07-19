from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import DebtPayment
from app.domain.enums import DebtType, PaymentMethod
from app.domain.repositories import DebtPaymentRepository
from app.domain.value_objects import Money
from app.infrastructure.models.debts import DebtPaymentModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: DebtPaymentModel) -> DebtPayment:
    return DebtPayment(
        id=model.id,
        debt_id=model.debt_id,
        debt_type=DebtType(model.debt_type),
        amount=Money(amount=Decimal(str(model.amount))),
        payment_method=PaymentMethod(model.payment_method),
        notes=model.notes or "",
        user_id=model.user_id,
        created_at=model.created_at,
    )


def _entity_to_model(entity: DebtPayment) -> DebtPaymentModel:
    return DebtPaymentModel(
        id=entity.id,
        debt_id=entity.debt_id,
        debt_type=entity.debt_type.value,
        amount=float(entity.amount.amount),
        payment_method=entity.payment_method.value,
        notes=entity.notes or None,
        user_id=entity.user_id,
        created_at=entity.created_at,
    )


class DebtPaymentRepositoryImpl(DebtPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, DebtPaymentModel)

    async def get_by_id(self, id: str) -> Optional[DebtPayment]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[DebtPayment], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: DebtPayment) -> DebtPayment:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: DebtPayment) -> DebtPayment:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.debt_id = entity.debt_id
            model.debt_type = entity.debt_type.value
            model.amount = float(entity.amount.amount)
            model.payment_method = entity.payment_method.value
            model.notes = entity.notes or None
            model.user_id = entity.user_id
            model.created_at = entity.created_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_debt(
        self, debt_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[DebtPayment], int]:
        count_stmt = (
            select(func.count())
            .select_from(DebtPaymentModel)
            .where(DebtPaymentModel.debt_id == debt_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(DebtPaymentModel)
            .where(DebtPaymentModel.debt_id == debt_id)
            .order_by(DebtPaymentModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
