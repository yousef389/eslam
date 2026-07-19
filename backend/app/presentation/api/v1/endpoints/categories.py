from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import CategoryCreate, CategoryUpdate
from app.application.use_cases.category_use_cases import (
    CreateCategoryUseCase,
    DeleteCategoryUseCase,
    ListCategoriesUseCase,
    UpdateCategoryUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.category_repository import CategoryRepositoryImpl

router = APIRouter()


def _require_write(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "staff"):
        raise ForbiddenException("Missing permission: categories:write")
    return user


def _category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "parent_id": category.parent_id,
        "is_active": category.is_active,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }


@router.get("/")
async def list_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = CategoryRepositoryImpl(db)
    use_case = ListCategoriesUseCase(repo)
    categories, total = await use_case.execute(page, per_page)
    return {
        "success": True,
        "data": [_category_to_dict(c) for c in categories],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/")
async def create_category(
    request: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = CategoryRepositoryImpl(db)
    use_case = CreateCategoryUseCase(repo)
    category = await use_case.execute(
        name=request.name,
        description=request.description,
        parent_id=request.parent_id,
    )
    return {"success": True, "data": _category_to_dict(category), "message": "Category created"}


@router.put("/{category_id}")
async def update_category(
    category_id: str,
    request: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = CategoryRepositoryImpl(db)
    use_case = UpdateCategoryUseCase(repo)
    category = await use_case.execute(
        category_id,
        name=request.name,
        description=request.description,
        parent_id=request.parent_id,
        is_active=request.is_active,
    )
    return {"success": True, "data": _category_to_dict(category), "message": "Category updated"}


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = CategoryRepositoryImpl(db)
    use_case = DeleteCategoryUseCase(repo)
    await use_case.execute(category_id)
    return {"success": True, "message": "Category deleted"}
