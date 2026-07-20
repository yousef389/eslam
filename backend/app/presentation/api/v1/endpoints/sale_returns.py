from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.sale_return_use_cases import (
    CreateSaleReturnUseCase,
    GetSaleReturnUseCase,
    ListSaleReturnsUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl
from app.infrastructure.repositories.sale_order_repository import SaleOrderRepositoryImpl
from app.infrastructure.repositories.sale_return_item_repository import SaleReturnItemRepositoryImpl
from app.infrastructure.repositories.sale_return_repository import SaleReturnRepositoryImpl

router = APIRouter()


class SaleReturnItemCreate(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class SaleReturnCreate(BaseModel):
    order_id: str
    items: List[SaleReturnItemCreate]
    reason: str = ""
    notes: str = ""


def _require_write(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "staff"):
        raise ForbiddenException("Missing permission: orders:write")
    return user


def _return_to_dict(sale_return, items=None):
    data = {
        "id": sale_return.id,
        "return_number": sale_return.return_number,
        "order_id": sale_return.order_id,
        "customer_id": sale_return.customer_id,
        "user_id": sale_return.user_id,
        "status": sale_return.status,
        "subtotal": float(sale_return.subtotal.amount),
        "tax_amount": float(sale_return.tax_amount.amount),
        "total": float(sale_return.total.amount),
        "reason": sale_return.reason,
        "notes": sale_return.notes,
        "created_at": sale_return.created_at.isoformat() if sale_return.created_at else None,
        "updated_at": sale_return.updated_at.isoformat() if sale_return.updated_at else None,
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
async def list_sale_returns(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SaleReturnRepositoryImpl(db)
    use_case = ListSaleReturnsUseCase(repo)
    returns, total = await use_case.execute(page, per_page)
    return {
        "success": True,
        "data": [_return_to_dict(r) for r in returns],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{return_id}")
async def get_sale_return(
    return_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    returns_repo = SaleReturnRepositoryImpl(db)
    items_repo = SaleReturnItemRepositoryImpl(db)
    use_case = GetSaleReturnUseCase(returns_repo, items_repo)
    result = await use_case.execute(return_id)
    return {
        "success": True,
        "data": _return_to_dict(result["sale_return"], result["items"]),
    }


@router.post("/")
async def create_sale_return(
    request: SaleReturnCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    returns_repo = SaleReturnRepositoryImpl(db)
    items_repo = SaleReturnItemRepositoryImpl(db)
    orders_repo = SaleOrderRepositoryImpl(db)
    products_repo = ProductRepositoryImpl(db)
    use_case = CreateSaleReturnUseCase(returns_repo, items_repo, orders_repo, products_repo)
    items_data = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        }
        for item in request.items
    ]
    sale_return = await use_case.execute(
        order_id=request.order_id,
        user_id=user["id"],
        items_data=items_data,
        reason=request.reason,
        notes=request.notes,
    )
    return {"success": True, "data": _return_to_dict(sale_return), "message": "Sale return created"}
