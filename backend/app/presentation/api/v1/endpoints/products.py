from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import ProductCreate, ProductUpdate
from app.application.use_cases.product_use_cases import (
    CreateProductUseCase,
    DeleteProductUseCase,
    GetLowStockProductsUseCase,
    GetProductUseCase,
    ListProductsUseCase,
    UpdateProductUseCase,
)
from app.core.dependencies import get_current_user, get_current_user_from_refresh
from app.core.exceptions import ForbiddenException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl

router = APIRouter()


def _require_write(user: dict):
    role = user.get("role", "")
    permissions = {
        "admin": True,
        "manager": True,
        "staff": True,
    }
    if not permissions.get(role, False):
        raise ForbiddenException("Missing permission: products:write")
    return user


def _product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "description": product.description,
        "category_id": product.category_id,
        "unit_price": float(product.unit_price.amount),
        "cost_price": float(product.cost_price.amount),
        "quantity_in_stock": product.quantity_in_stock,
        "minimum_stock_level": product.minimum_stock_level,
        "maximum_stock_level": product.maximum_stock_level,
        "unit": product.unit,
        "is_active": product.is_active,
        "image_url": product.image_url,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


@router.get("/low-stock")
async def get_low_stock(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ProductRepositoryImpl(db)
    use_case = GetLowStockProductsUseCase(repo)
    products, total = await use_case.execute(page, per_page)
    return {
        "success": True,
        "data": [_product_to_dict(p) for p in products],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/")
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ProductRepositoryImpl(db)
    use_case = ListProductsUseCase(repo)
    products, total = await use_case.execute(page, per_page, search)
    return {
        "success": True,
        "data": [_product_to_dict(p) for p in products],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ProductRepositoryImpl(db)
    use_case = GetProductUseCase(repo)
    product = await use_case.execute(product_id)
    return {"success": True, "data": _product_to_dict(product)}


@router.post("/")
async def create_product(
    request: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = ProductRepositoryImpl(db)
    use_case = CreateProductUseCase(repo)
    product = await use_case.execute(
        name=request.name,
        sku=request.sku,
        unit_price=request.unit_price,
        cost_price=request.cost_price,
        quantity_in_stock=request.quantity_in_stock,
        minimum_stock_level=request.minimum_stock_level,
        maximum_stock_level=request.maximum_stock_level,
        unit=request.unit,
        barcode=request.barcode,
        description=request.description,
        category_id=request.category_id,
        image_url=request.image_url,
    )
    return {"success": True, "data": _product_to_dict(product), "message": "Product created"}


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    request: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = ProductRepositoryImpl(db)
    use_case = UpdateProductUseCase(repo)
    updates = request.model_dump(exclude_unset=True)
    product = await use_case.execute(product_id, updates)
    return {"success": True, "data": _product_to_dict(product), "message": "Product updated"}


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = ProductRepositoryImpl(db)
    use_case = DeleteProductUseCase(repo)
    await use_case.execute(product_id)
    return {"success": True, "message": "Product deleted"}
