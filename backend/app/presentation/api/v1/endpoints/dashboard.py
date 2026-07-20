from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.dashboard_use_cases import GetDashboardStatsUseCase
from app.core.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.repositories.cashbox_repository import CashboxRepositoryImpl
from app.infrastructure.repositories.customer_debt_repository import CustomerDebtRepositoryImpl
from app.infrastructure.repositories.customer_repository import CustomerRepositoryImpl
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl
from app.infrastructure.repositories.purchase_order_repository import PurchaseOrderRepositoryImpl
from app.infrastructure.repositories.sale_order_repository import SaleOrderRepositoryImpl
from app.infrastructure.repositories.supplier_debt_repository import SupplierDebtRepositoryImpl

router = APIRouter()


def _stats_to_dict(stats):
    return {
        "daily_sales": float(stats["daily_sales"]),
        "monthly_sales": float(stats["monthly_sales"]),
        "total_products": stats["total_products"],
        "total_customers": stats["total_customers"],
        "low_stock_items": stats["low_stock_items"],
        "pending_orders": stats["pending_orders"],
        "total_purchases": float(stats["total_purchases"]),
        "net_profit": float(stats["net_profit"]),
        "cashbox_balance": float(stats["cashbox_balance"]),
        "customer_debts_total": float(stats["customer_debts_total"]),
        "supplier_debts_total": float(stats["supplier_debts_total"]),
        "invoice_count": stats["invoice_count"],
        "recent_activities": stats["recent_activities"],
    }


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    sale_orders_repo = SaleOrderRepositoryImpl(db)
    purchase_orders_repo = PurchaseOrderRepositoryImpl(db)
    products_repo = ProductRepositoryImpl(db)
    customers_repo = CustomerRepositoryImpl(db)
    cashbox_repo = CashboxRepositoryImpl(db)
    customer_debt_repo = CustomerDebtRepositoryImpl(db)
    supplier_debt_repo = SupplierDebtRepositoryImpl(db)
    use_case = GetDashboardStatsUseCase(
        sale_orders_repo,
        purchase_orders_repo,
        products_repo,
        customers_repo,
        cashbox_repo,
        customer_debt_repo,
        supplier_debt_repo,
    )
    stats = await use_case.execute()
    return {"success": True, "data": _stats_to_dict(stats)}
