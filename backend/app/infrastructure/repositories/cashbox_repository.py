from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Cashbox
from app.domain.repositories import CashboxRepository
from app.domain.value_objects import Money
from app.infrastructure.models.cashbox import CashboxModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: CashboxModel) -> Cashbox:
    return Cashbox(
        id=model.id,
        name=model.name,
        balance=Money(amount=Decimal(str(model.balance))),
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: Cashbox) -> CashboxModel:
    return CashboxModel(
        id=entity.id,
        name=entity.name,
        balance=float(entity.balance.amount),
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class CashboxRepositoryImpl(CashboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, CashboxModel)

    async def get_by_id(self, id: str) -> Optional[Cashbox]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Cashbox], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: Cashbox) -> Cashbox:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: Cashbox) -> Cashbox:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.name = entity.name
            model.balance = float(entity.balance.amount)
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_default(self) -> Optional[Cashbox]:
        stmt = select(CashboxModel).where(CashboxModel.is_active == True).limit(1)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None
