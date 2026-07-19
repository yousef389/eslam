from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import CashboxTransaction
from app.domain.enums import TransactionType
from app.domain.repositories import CashboxTransactionRepository
from app.domain.value_objects import Money
from app.infrastructure.models.cashbox import CashboxTransactionModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: CashboxTransactionModel) -> CashboxTransaction:
    return CashboxTransaction(
        id=model.id,
        cashbox_id=model.cashbox_id,
        transaction_type=TransactionType(model.transaction_type),
        amount=Money(amount=Decimal(str(model.amount))),
        description=model.description,
        reference_id=model.reference_id,
        user_id=model.user_id,
        created_at=model.created_at,
    )


def _entity_to_model(entity: CashboxTransaction) -> CashboxTransactionModel:
    return CashboxTransactionModel(
        id=entity.id,
        cashbox_id=entity.cashbox_id,
        transaction_type=entity.transaction_type.value,
        amount=float(entity.amount.amount),
        description=entity.description,
        reference_id=entity.reference_id,
        user_id=entity.user_id,
        created_at=entity.created_at,
    )


class CashboxTransactionRepositoryImpl(CashboxTransactionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, CashboxTransactionModel)

    async def get_by_id(self, id: str) -> Optional[CashboxTransaction]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[CashboxTransaction], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: CashboxTransaction) -> CashboxTransaction:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: CashboxTransaction) -> CashboxTransaction:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.cashbox_id = entity.cashbox_id
            model.transaction_type = entity.transaction_type.value
            model.amount = float(entity.amount.amount)
            model.description = entity.description
            model.reference_id = entity.reference_id
            model.user_id = entity.user_id
            model.created_at = entity.created_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_cashbox(
        self, cashbox_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CashboxTransaction], int]:
        count_stmt = (
            select(func.count())
            .select_from(CashboxTransactionModel)
            .where(CashboxTransactionModel.cashbox_id == cashbox_id)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(CashboxTransactionModel)
            .where(CashboxTransactionModel.cashbox_id == cashbox_id)
            .order_by(CashboxTransactionModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CashboxTransaction], int]:
        base_filter = CashboxTransactionModel.created_at.between(start_date, end_date)

        count_stmt = select(func.count()).select_from(CashboxTransactionModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(CashboxTransactionModel)
            .where(base_filter)
            .order_by(CashboxTransactionModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
