from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Supplier
from app.domain.repositories import SupplierRepository
from app.domain.value_objects import Money
from app.infrastructure.models.suppliers import SupplierModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: SupplierModel) -> Supplier:
    return Supplier(
        id=model.id,
        name=model.name,
        phone=model.phone,
        email=model.email,
        address=model.address,
        tax_number=model.tax_number,
        payment_terms_days=model.payment_terms_days,
        is_active=model.is_active,
        notes=model.notes or "",
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: Supplier) -> SupplierModel:
    return SupplierModel(
        id=entity.id,
        name=entity.name,
        phone=entity.phone,
        email=entity.email,
        address=entity.address if isinstance(entity.address, str) else str(entity.address) if entity.address else None,
        tax_number=entity.tax_number,
        payment_terms_days=entity.payment_terms_days,
        is_active=entity.is_active,
        notes=entity.notes or None,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SupplierRepositoryImpl(SupplierRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, SupplierModel)

    async def get_by_id(self, id: str) -> Optional[Supplier]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Supplier], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: Supplier) -> Supplier:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: Supplier) -> Supplier:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.name = entity.name
            model.phone = entity.phone
            model.email = entity.email
            model.address = entity.address if isinstance(entity.address, str) else str(entity.address) if entity.address else None
            model.tax_number = entity.tax_number
            model.payment_terms_days = entity.payment_terms_days
            model.is_active = entity.is_active
            model.notes = entity.notes or None
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[Supplier], int]:
        pattern = f"%{query}%"
        base_filter = SupplierModel.name.ilike(pattern) | SupplierModel.phone.ilike(pattern)

        count_stmt = select(func.count()).select_from(SupplierModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SupplierModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_name(self, name: str) -> Optional[Supplier]:
        stmt = select(SupplierModel).where(SupplierModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None
