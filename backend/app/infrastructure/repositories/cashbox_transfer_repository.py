from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import CashboxTransferRepository
from app.domain.entities import CashboxTransfer
from app.domain.value_objects import Money
from app.infrastructure.models.inventory import CashboxTransferModel


class CashboxTransferRepositoryImpl(CashboxTransferRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: str) -> Optional[CashboxTransfer]:
        stmt = select(CashboxTransferModel).where(CashboxTransferModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[CashboxTransfer], int]:
        count_stmt = select(func.count()).select_from(CashboxTransferModel)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(CashboxTransferModel).order_by(CashboxTransferModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def create(self, entity: CashboxTransfer) -> CashboxTransfer:
        model = CashboxTransferModel(
            id=entity.id, transfer_number=entity.transfer_number,
            from_cashbox_id=entity.from_cashbox_id, to_cashbox_id=entity.to_cashbox_id,
            amount=float(entity.amount.amount), description=entity.description,
            user_id=entity.user_id, created_at=entity.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: CashboxTransfer) -> CashboxTransfer:
        return entity

    async def delete(self, id: str) -> bool:
        stmt = select(CashboxTransferModel).where(CashboxTransferModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def get_by_from_cashbox(self, cashbox_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[CashboxTransfer], int]:
        count_stmt = select(func.count()).select_from(CashboxTransferModel).where(CashboxTransferModel.from_cashbox_id == cashbox_id)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(CashboxTransferModel).where(CashboxTransferModel.from_cashbox_id == cashbox_id).order_by(CashboxTransferModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def get_by_to_cashbox(self, cashbox_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[CashboxTransfer], int]:
        count_stmt = select(func.count()).select_from(CashboxTransferModel).where(CashboxTransferModel.to_cashbox_id == cashbox_id)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        stmt = select(CashboxTransferModel).where(CashboxTransferModel.to_cashbox_id == cashbox_id).order_by(CashboxTransferModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    def _to_entity(self, m: CashboxTransferModel) -> CashboxTransfer:
        return CashboxTransfer(
            id=m.id, transfer_number=m.transfer_number,
            from_cashbox_id=m.from_cashbox_id, to_cashbox_id=m.to_cashbox_id,
            amount=Money(amount=m.amount), description=m.description or "",
            user_id=m.user_id, created_at=m.created_at,
        )
