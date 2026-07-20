from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import PurchaseOrderCreate
from app.application.use_cases.purchase_order_use_cases import (
    CreatePurchaseOrderUseCase,
    DeletePurchaseOrderUseCase,
    GetPurchaseOrderUseCase,
    ListPurchaseOrdersUseCase,
    SearchPurchaseOrdersUseCase,
    UpdatePurchaseOrderStatusUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl
from app.infrastructure.repositories.purchase_order_item_repository import PurchaseOrderItemRepositoryImpl
from app.infrastructure.repositories.purchase_order_repository import PurchaseOrderRepositoryImpl
from app.infrastructure.repositories.supplier_repository import SupplierRepositoryImpl

router = APIRouter()


class UpdateOrderStatusRequest(BaseModel):
    status: str


def _require_write(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "staff"):
        raise ForbiddenException("Missing permission: orders:write")
    return user


def _order_to_dict(order, items=None):
    data = {
        "id": order.id,
        "order_number": order.order_number,
        "supplier_id": order.supplier_id,
        "user_id": order.user_id,
        "status": order.status.value if hasattr(order.status, "value") else order.status,
        "subtotal": float(order.subtotal.amount),
        "discount": float(order.discount.amount),
        "tax_amount": float(order.tax_amount.amount),
        "total": float(order.total.amount),
        "payment_method": order.payment_method.value if order.payment_method and hasattr(order.payment_method, "value") else order.payment_method,
        "notes": order.notes,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }
    if items is not None:
        data["items"] = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price.amount),
                "discount": float(item.discount.amount),
                "total": float(item.total.amount),
            }
            for item in items
        ]
    return data


@router.get("/")
async def list_purchase_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = PurchaseOrderRepositoryImpl(db)
    if search:
        use_case = SearchPurchaseOrdersUseCase(repo)
        orders, total = await use_case.execute(search, page, per_page)
    else:
        use_case = ListPurchaseOrdersUseCase(repo)
        orders, total = await use_case.execute(page, per_page, from_date, to_date)
    return {
        "success": True,
        "data": [_order_to_dict(o) for o in orders],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{order_id}")
async def get_purchase_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    orders_repo = PurchaseOrderRepositoryImpl(db)
    items_repo = PurchaseOrderItemRepositoryImpl(db)
    use_case = GetPurchaseOrderUseCase(orders_repo, items_repo)
    result = await use_case.execute(order_id)
    return {
        "success": True,
        "data": _order_to_dict(result["order"], result["items"]),
    }


@router.post("/")
async def create_purchase_order(
    request: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    orders_repo = PurchaseOrderRepositoryImpl(db)
    items_repo = PurchaseOrderItemRepositoryImpl(db)
    products_repo = ProductRepositoryImpl(db)
    suppliers_repo = SupplierRepositoryImpl(db)
    use_case = CreatePurchaseOrderUseCase(orders_repo, items_repo, products_repo, suppliers_repo)
    items_data = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "discount": item.discount,
        }
        for item in request.items
    ]
    order = await use_case.execute(
        supplier_id=request.supplier_id,
        user_id=user["id"],
        items_data=items_data,
        discount=request.discount,
        tax_rate=request.tax_rate,
        payment_method=request.payment_method,
        notes=request.notes,
    )
    return {"success": True, "data": _order_to_dict(order), "message": "Purchase order created"}


@router.put("/{order_id}/status")
async def update_purchase_order_status(
    order_id: str,
    request: UpdateOrderStatusRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    orders_repo = PurchaseOrderRepositoryImpl(db)
    products_repo = ProductRepositoryImpl(db)
    items_repo = PurchaseOrderItemRepositoryImpl(db)
    use_case = UpdatePurchaseOrderStatusUseCase(orders_repo, products_repo)
    order = await use_case.execute(order_id, request.status, items_repo)
    return {"success": True, "data": _order_to_dict(order), "message": "Order status updated"}


@router.delete("/{order_id}")
async def delete_purchase_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    orders_repo = PurchaseOrderRepositoryImpl(db)
    items_repo = PurchaseOrderItemRepositoryImpl(db)
    products_repo = ProductRepositoryImpl(db)
    use_case = DeletePurchaseOrderUseCase(orders_repo, items_repo, products_repo)
    await use_case.execute(order_id)
    return {"success": True, "message": "Purchase order deleted"}
