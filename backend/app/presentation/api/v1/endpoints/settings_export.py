import json
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.repositories.system_setting_repository import SystemSettingRepositoryImpl
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl
from app.infrastructure.repositories.customer_repository import CustomerRepositoryImpl
from app.infrastructure.repositories.supplier_repository import SupplierRepositoryImpl
from app.infrastructure.repositories.sale_order_repository import SaleOrderRepositoryImpl
from app.infrastructure.repositories.purchase_order_repository import PurchaseOrderRepositoryImpl

router = APIRouter()


@router.get("/backup")
async def backup_data(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    products_repo = ProductRepositoryImpl(db)
    customers_repo = CustomerRepositoryImpl(db)
    suppliers_repo = SupplierRepositoryImpl(db)
    settings_repo = SystemSettingRepositoryImpl(db)

    products, _ = await products_repo.get_all(page=1, per_page=10000)
    customers, _ = await customers_repo.get_all(page=1, per_page=10000)
    suppliers, _ = await suppliers_repo.get_all(page=1, per_page=10000)
    settings = await settings_repo.get_all_settings()

    backup = {
        "version": "1.0",
        "created_at": datetime.utcnow().isoformat(),
        "created_by": user.get("username", "unknown"),
        "products": [
            {
                "name": p.name, "sku": p.sku, "barcode": p.barcode,
                "category_id": p.category_id, "supplier_id": p.supplier_id,
                "unit_price": float(p.unit_price.amount), "cost_price": float(p.cost_price.amount),
                "quantity_in_stock": p.quantity_in_stock, "unit": p.unit,
            }
            for p in products
        ],
        "customers": [
            {"name": c.name, "phone": c.phone, "email": c.email, "address": str(c.address) if c.address else None}
            for c in customers
        ],
        "suppliers": [
            {"name": s.name, "phone": s.phone, "email": s.email, "address": str(s.address) if s.address else None}
            for s in suppliers
        ],
        "settings": [
            {"key": s.key, "value": s.value, "group": s.group.value if hasattr(s.group, 'value') else s.group}
            for s in settings
        ],
    }

    content = json.dumps(backup, ensure_ascii=False, indent=2)
    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"},
    )


@router.get("/export/products")
async def export_products(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.application.services.export_service import ExportService

    repo = ProductRepositoryImpl(db)
    products, _ = await repo.get_all(page=1, per_page=10000)

    data = [
        {
            "id": p.id, "name": p.name, "sku": p.sku, "barcode": p.barcode,
            "category_id": p.category_id, "supplier_id": p.supplier_id,
            "unit_price": float(p.unit_price.amount), "cost_price": float(p.cost_price.amount),
            "quantity_in_stock": p.quantity_in_stock, "unit": p.unit, "is_active": p.is_active,
        }
        for p in products
    ]

    export_service = ExportService()
    content = export_service.export_to_csv(data, "products")
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products_export.csv"},
    )


@router.get("/export/customers")
async def export_customers(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.application.services.export_service import ExportService

    repo = CustomerRepositoryImpl(db)
    customers, _ = await repo.get_all(page=1, per_page=10000)

    data = [
        {"id": c.id, "name": c.name, "phone": c.phone, "email": c.email}
        for c in customers
    ]

    export_service = ExportService()
    content = export_service.export_to_csv(data, "customers")
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=customers_export.csv"},
    )


@router.get("/export/suppliers")
async def export_suppliers(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.application.services.export_service import ExportService

    repo = SupplierRepositoryImpl(db)
    suppliers, _ = await repo.get_all(page=1, per_page=10000)

    data = [
        {"id": s.id, "name": s.name, "phone": s.phone, "email": s.email}
        for s in suppliers
    ]

    export_service = ExportService()
    content = export_service.export_to_csv(data, "suppliers")
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=suppliers_export.csv"},
    )
