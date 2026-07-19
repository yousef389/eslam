from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Category
from app.domain.repositories import CategoryRepository
from app.infrastructure.models.categories import CategoryModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: CategoryModel) -> Category:
    return Category(
        id=model.id,
        name=model.name,
        description=model.description or "",
        parent_id=model.parent_id,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: Category) -> CategoryModel:
    return CategoryModel(
        id=entity.id,
        name=entity.name,
        description=entity.description or None,
        parent_id=entity.parent_id,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class CategoryRepositoryImpl(CategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, CategoryModel)

    async def get_by_id(self, id: str) -> Optional[Category]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Category], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: Category) -> Category:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: Category) -> Category:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.name = entity.name
            model.description = entity.description or None
            model.parent_id = entity.parent_id
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_name(self, name: str) -> Optional[Category]:
        stmt = select(CategoryModel).where(CategoryModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None
