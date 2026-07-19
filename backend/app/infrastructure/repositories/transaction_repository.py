from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Transaction
from app.domain.enums import TransactionType
from app.domain.repositories import TransactionRepository
from app.domain.value_objects import Money
from app.infrastructure.models.transactions import TransactionModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: TransactionModel) -> Transaction:
    return Transaction(
        id=model.id,
        transaction_number=model.transaction_number,
        type=TransactionType(model.type),
        amount=Money(amount=Decimal(str(model.amount))),
        description=model.description,
        reference_id=model.reference_id,
        reference_type=model.reference_type,
        user_id=model.user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: Transaction) -> TransactionModel:
    return TransactionModel(
        id=entity.id,
        transaction_number=entity.transaction_number,
        type=entity.type.value,
        amount=float(entity.amount.amount),
        description=entity.description,
        reference_id=entity.reference_id,
        reference_type=entity.reference_type,
        user_id=entity.user_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class TransactionRepositoryImpl(TransactionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, TransactionModel)

    async def get_by_id(self, id: str) -> Optional[Transaction]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Transaction], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: Transaction) -> Transaction:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: Transaction) -> Transaction:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.transaction_number = entity.transaction_number
            model.type = entity.type.value
            model.amount = float(entity.amount.amount)
            model.description = entity.description
            model.reference_id = entity.reference_id
            model.reference_type = entity.reference_type
            model.user_id = entity.user_id
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Transaction], int]:
        base_filter = TransactionModel.created_at.between(start_date, end_date)

        count_stmt = select(func.count()).select_from(TransactionModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(TransactionModel)
            .where(base_filter)
            .order_by(TransactionModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_type(
        self, tx_type: TransactionType, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Transaction], int]:
        count_stmt = (
            select(func.count())
            .select_from(TransactionModel)
            .where(TransactionModel.type == tx_type.value)
        )
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(TransactionModel)
            .where(TransactionModel.type == tx_type.value)
            .order_by(TransactionModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_summary(self, start_date: datetime, end_date: datetime) -> dict:
        base_filter = TransactionModel.created_at.between(start_date, end_date)

        total_stmt = select(
            func.coalesce(func.sum(TransactionModel.amount), 0),
            func.count(TransactionModel.id),
        ).where(base_filter)
        result = await self._session.execute(total_stmt)
        row = result.one()
        total_amount = Decimal(str(row[0]))
        total_count = row[1]

        income_stmt = select(
            func.coalesce(func.sum(TransactionModel.amount), 0),
        ).where(base_filter, TransactionModel.type == TransactionType.INCOME.value)
        income_result = await self._session.execute(income_stmt)
        income = Decimal(str(income_result.scalar()))

        expense_stmt = select(
            func.coalesce(func.sum(TransactionModel.amount), 0),
        ).where(base_filter, TransactionModel.type == TransactionType.EXPENSE.value)
        expense_result = await self._session.execute(expense_stmt)
        expense = Decimal(str(expense_result.scalar()))

        return {
            "total_amount": total_amount,
            "total_count": total_count,
            "income": income,
            "expense": expense,
            "net": income - expense,
        }
