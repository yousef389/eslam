from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.models.products import ProductModel
from app.infrastructure.models.customers import CustomerModel
from app.infrastructure.models.suppliers import SupplierModel
from app.infrastructure.models.sale_orders import SaleOrderModel
from app.infrastructure.models.purchase_orders import PurchaseOrderModel

router = APIRouter()


@router.get("/")
async def global_search(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    results = []

    # Search products
    stmt = (
        select(ProductModel)
        .where(
            or_(
                ProductModel.name.ilike(f"%{q}%"),
                ProductModel.sku.ilike(f"%{q}%"),
                ProductModel.barcode.ilike(f"%{q}%"),
            )
        )
        .limit(5)
    )
    result = await db.execute(stmt)
    for p in result.scalars().all():
        results.append(
            {
                "id": p.id,
                "name": p.name,
                "type": "product",
                "link": f"/products/{p.id}",
                "subtitle": p.sku,
            }
        )

    # Search customers
    stmt = (
        select(CustomerModel)
        .where(
            or_(
                CustomerModel.name.ilike(f"%{q}%"),
                CustomerModel.phone.ilike(f"%{q}%"),
            )
        )
        .limit(5)
    )
    result = await db.execute(stmt)
    for c in result.scalars().all():
        results.append(
            {
                "id": c.id,
                "name": c.name,
                "type": "customer",
                "link": f"/customers/{c.id}",
                "subtitle": c.phone,
            }
        )

    # Search suppliers
    stmt = (
        select(SupplierModel)
        .where(
            or_(
                SupplierModel.name.ilike(f"%{q}%"),
                SupplierModel.phone.ilike(f"%{q}%"),
            )
        )
        .limit(5)
    )
    result = await db.execute(stmt)
    for s in result.scalars().all():
        results.append(
            {
                "id": s.id,
                "name": s.name,
                "type": "supplier",
                "link": f"/suppliers/{s.id}",
                "subtitle": s.phone,
            }
        )

    # Search sale orders
    stmt = (
        select(SaleOrderModel)
        .where(SaleOrderModel.order_number.ilike(f"%{q}%"))
        .limit(5)
    )
    result = await db.execute(stmt)
    for o in result.scalars().all():
        results.append(
            {
                "id": o.id,
                "name": o.order_number,
                "type": "sale_order",
                "link": f"/sales/{o.id}",
                "subtitle": f"Total: {o.total}",
            }
        )

    # Search purchase orders
    stmt = (
        select(PurchaseOrderModel)
        .where(PurchaseOrderModel.order_number.ilike(f"%{q}%"))
        .limit(5)
    )
    result = await db.execute(stmt)
    for o in result.scalars().all():
        results.append(
            {
                "id": o.id,
                "name": o.order_number,
                "type": "purchase_order",
                "link": f"/purchases/{o.id}",
                "subtitle": f"Total: {o.total}",
            }
        )

    return {"success": True, "data": results}
