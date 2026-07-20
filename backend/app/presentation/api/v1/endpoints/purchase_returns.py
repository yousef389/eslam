from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import PurchaseReturnCreate
from app.application.use_cases.purchase_return_use_cases import (
    CreatePurchaseReturnUseCase,
    GetPurchaseReturnUseCase,
    ListPurchaseReturnsUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl
from app.infrastructure.repositories.purchase_order_item_repository import PurchaseOrderItemRepositoryImpl
from app.infrastructure.repositories.purchase_order_repository import PurchaseOrderRepositoryImpl
from app.infrastructure.repositories.purchase_return_item_repository import PurchaseReturnItemRepositoryImpl
from app.infrastructure.repositories.purchase_return_repository import PurchaseReturnRepositoryImpl
from app.infrastructure.repositories.supplier_repository import SupplierRepositoryImpl

router = APIRouter()


def _require_write(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "staff"):
        raise ForbiddenException("Missing permission: orders:write")
    return user


def _return_to_dict(purchase_return, items=None):
    data = {
        "id": purchase_return.id,
        "return_number": purchase_return.return_number,
        "order_id": purchase_return.order_id,
        "supplier_id": purchase_return.supplier_id,
        "user_id": purchase_return.user_id,
        "status": purchase_return.status,
        "subtotal": float(purchase_return.subtotal.amount),
        "tax_amount": float(purchase_return.tax_amount.amount),
        "total": float(purchase_return.total.amount),
        "reason": purchase_return.reason,
        "notes": purchase_return.notes,
        "created_at": purchase_return.created_at.isoformat() if purchase_return.created_at else None,
        "updated_at": purchase_return.updated_at.isoformat() if purchase_return.updated_at else None,
    }
    if items is not None:
        data["items"] = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price.amount),
                "total": float(item.total.amount),
            }
            for item in items
        ]
    return data


@router.get("/")
async def list_purchase_returns(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = PurchaseReturnRepositoryImpl(db)
    use_case = ListPurchaseReturnsUseCase(repo)
    returns, total = await use_case.execute(page, per_page)
    return {
        "success": True,
        "data": [_return_to_dict(r) for r in returns],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{return_id}")
async def get_purchase_return(
    return_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    returns_repo = PurchaseReturnRepositoryImpl(db)
    items_repo = PurchaseReturnItemRepositoryImpl(db)
    use_case = GetPurchaseReturnUseCase(returns_repo, items_repo)
    result = await use_case.execute(return_id)
    return {
        "success": True,
        "data": _return_to_dict(result["return"], result["items"]),
    }


@router.post("/")
async def create_purchase_return(
    request: PurchaseReturnCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    returns_repo = PurchaseReturnRepositoryImpl(db)
    items_repo = PurchaseReturnItemRepositoryImpl(db)
    orders_repo = PurchaseOrderRepositoryImpl(db)
    order_items_repo = PurchaseOrderItemRepositoryImpl(db)
    products_repo = ProductRepositoryImpl(db)
    suppliers_repo = SupplierRepositoryImpl(db)
    use_case = CreatePurchaseReturnUseCase(
        returns_repo, items_repo, orders_repo, order_items_repo, products_repo, suppliers_repo
    )
    items_data = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        }
        for item in request.items
    ]
    purchase_return = await use_case.execute(
        order_id=request.order_id,
        supplier_id=request.supplier_id,
        user_id=user["id"],
        items_data=items_data,
        reason=request.reason or "",
        notes=request.notes,
    )
    return {"success": True, "data": _return_to_dict(purchase_return), "message": "Purchase return created"}
