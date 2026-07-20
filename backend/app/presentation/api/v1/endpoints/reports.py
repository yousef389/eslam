from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.export_service import ExportService
from app.core.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sale_order_repository import SaleOrderRepositoryImpl
from app.infrastructure.repositories.purchase_order_repository import PurchaseOrderRepositoryImpl
from app.infrastructure.repositories.customer_debt_repository import CustomerDebtRepositoryImpl
from app.infrastructure.repositories.supplier_debt_repository import SupplierDebtRepositoryImpl
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl

import io

router = APIRouter()


@router.get("/sales/excel")
async def export_sales_excel(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SaleOrderRepositoryImpl(db)
    if from_date and to_date:
        orders, _ = await repo.get_by_date_range(from_date, to_date, page=1, per_page=100000)
    else:
        orders, _ = await repo.get_all(page=1, per_page=100000)

    data = [
        {
            "رقم الفاتورة": o.order_number,
            "التاريخ": o.created_at.strftime("%Y-%m-%d") if o.created_at else "",
            "الإجمالي": float(o.total.amount),
            "الخصم": float(o.discount.amount),
            "الضريبة": float(o.tax_amount.amount),
            "الحالة": o.status.value if hasattr(o.status, "value") else o.status,
            "طريقة الدفع": o.payment_method.value if o.payment_method else "",
        }
        for o in orders
    ]
    file_content = ExportService.export_to_excel(data)
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=sales_report.xlsx"},
    )


@router.get("/sales/pdf")
async def export_sales_pdf(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SaleOrderRepositoryImpl(db)
    if from_date and to_date:
        orders, _ = await repo.get_by_date_range(from_date, to_date, page=1, per_page=100000)
    else:
        orders, _ = await repo.get_all(page=1, per_page=100000)

    data = [
        {
            "Order #": o.order_number,
            "Date": o.created_at.strftime("%Y-%m-%d") if o.created_at else "",
            "Total": f"{float(o.total.amount):.2f}",
            "Discount": f"{float(o.discount.amount):.2f}",
            "Tax": f"{float(o.tax_amount.amount):.2f}",
            "Status": o.status.value if hasattr(o.status, "value") else o.status,
        }
        for o in orders
    ]
    file_content = ExportService.export_to_pdf(data, title="Sales Report")
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sales_report.pdf"},
    )


@router.get("/purchases/excel")
async def export_purchases_excel(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = PurchaseOrderRepositoryImpl(db)
    if from_date and to_date:
        orders, _ = await repo.get_by_date_range(from_date, to_date, page=1, per_page=100000)
    else:
        orders, _ = await repo.get_all(page=1, per_page=100000)

    data = [
        {
            "رقم الفاتورة": o.order_number,
            "التاريخ": o.created_at.strftime("%Y-%m-%d") if o.created_at else "",
            "الإجمالي": float(o.total.amount),
            "الخصم": float(o.discount.amount),
            "الحالة": o.status.value if hasattr(o.status, "value") else o.status,
        }
        for o in orders
    ]
    file_content = ExportService.export_to_excel(data)
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=purchases_report.xlsx"},
    )


@router.get("/inventory/excel")
async def export_inventory_excel(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ProductRepositoryImpl(db)
    products, _ = await repo.get_all(page=1, per_page=100000)

    data = [
        {
            "اسم المنتج": p.name,
            "SKU": p.sku,
            "الباركود": p.barcode or "",
            "الكمية": p.quantity_in_stock,
            "الحد الأدنى": p.minimum_stock_level,
            "سعر الشراء": float(p.cost_price.amount),
            "سعر البيع": float(p.unit_price.amount),
            "الحالة": "ناقص" if p.quantity_in_stock <= p.minimum_stock_level else "متوفر",
        }
        for p in products
    ]
    file_content = ExportService.export_to_excel(data)
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventory_report.xlsx"},
    )


@router.get("/customers/excel")
async def export_customers_excel(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.infrastructure.repositories.customer_repository import CustomerRepositoryImpl
    repo = CustomerRepositoryImpl(db)
    customers, _ = await repo.get_all(page=1, per_page=100000)

    data = [
        {
            "اسم العميل": c.name,
            "الهاتف": c.phone,
            "البريد": c.email or "",
            "الرصيد": float(c.current_balance.amount),
        }
        for c in customers
    ]
    file_content = ExportService.export_to_excel(data)
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=customers_report.xlsx"},
    )
