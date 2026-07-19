from fastapi import APIRouter

from app.presentation.api.v1.endpoints import (
    auth,
    products,
    categories,
    customers,
    suppliers,
    sale_orders,
    purchase_orders,
    dashboard,
    accounting_customers,
    accounting_suppliers,
    accounting_cashbox,
    accounting_reports,
    extractions,
)

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(customers.router, prefix="/customers", tags=["Customers"])
router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
router.include_router(sale_orders.router, prefix="/sale-orders", tags=["Sale Orders"])
router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(accounting_customers.router, prefix="/accounting/customers", tags=["Customer Accounts"])
router.include_router(accounting_suppliers.router, prefix="/accounting/suppliers", tags=["Supplier Accounts"])
router.include_router(accounting_cashbox.router, prefix="/accounting/cashbox", tags=["Cashbox"])
router.include_router(accounting_reports.router, prefix="/accounting/reports", tags=["Financial Reports"])
router.include_router(extractions.router, prefix="/extractions", tags=["AI Extractions"])
