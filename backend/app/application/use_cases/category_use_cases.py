from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException
from app.domain.entities import Category


class ListCategoriesUseCase:
    def __init__(self, categories_repo):
        self.categories_repo = categories_repo

    async def execute(
        self, page: int = 1, per_page: int = 20
    ) -> Tuple[list, int]:
        return await self.categories_repo.get_all(page, per_page)


class GetCategoryUseCase:
    def __init__(self, categories_repo):
        self.categories_repo = categories_repo

    async def execute(self, category_id: str) -> Category:
        category = await self.categories_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category


class CreateCategoryUseCase:
    def __init__(self, categories_repo):
        self.categories_repo = categories_repo

    async def execute(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> Category:
        existing = await self.categories_repo.get_by_name(name)
        if existing:
            raise ConflictException(f"Category '{name}' already exists")

        if parent_id:
            parent = await self.categories_repo.get_by_id(parent_id)
            if not parent:
                raise NotFoundException("Parent category", parent_id)

        category = Category(
            name=name,
            description=description or "",
            parent_id=parent_id,
        )

        return await self.categories_repo.create(category)


class UpdateCategoryUseCase:
    def __init__(self, categories_repo):
        self.categories_repo = categories_repo

    async def execute(
        self,
        category_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Category:
        category = await self.categories_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)

        if name is not None:
            existing = await self.categories_repo.get_by_name(name)
            if existing and existing.id != category_id:
                raise ConflictException(f"Category name '{name}' already in use")
            category.name = name

        if description is not None:
            category.description = description
        if parent_id is not None:
            if parent_id == category_id:
                raise ConflictException("Category cannot be its own parent")
            if parent_id:
                parent = await self.categories_repo.get_by_id(parent_id)
                if not parent:
                    raise NotFoundException("Parent category", parent_id)
            category.parent_id = parent_id
        if is_active is not None:
            category.is_active = is_active

        category.updated_at = datetime.utcnow()
        return await self.categories_repo.update(category)


class DeleteCategoryUseCase:
    def __init__(self, categories_repo):
        self.categories_repo = categories_repo

    async def execute(self, category_id: str) -> None:
        category = await self.categories_repo.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)

        category.is_active = False
        category.updated_at = datetime.utcnow()
        await self.categories_repo.update(category)
