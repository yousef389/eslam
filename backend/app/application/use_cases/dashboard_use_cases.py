from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, select

from app.domain.enums import DebtStatus, OrderStatus
from app.infrastructure.models.debts import CustomerDebtModel, SupplierDebtModel
from app.infrastructure.models.cashbox import CashboxModel
from app.infrastructure.models.sale_orders import SaleOrderModel


class GetDashboardStatsUseCase:
    def __init__(
        self,
        sale_orders_repo,
        purchase_orders_repo,
        products_repo,
        customers_repo,
        cashbox_repo,
        customer_debt_repo,
        supplier_debt_repo,
    ):
        self.sale_orders_repo = sale_orders_repo
        self.purchase_orders_repo = purchase_orders_repo
        self.products_repo = products_repo
        self.customers_repo = customers_repo
        self.cashbox_repo = cashbox_repo
        self.customer_debt_repo = customer_debt_repo
        self.supplier_debt_repo = supplier_debt_repo

    async def execute(self) -> dict:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        daily_sales = await self.sale_orders_repo.get_daily_sales(today_start)

        monthly_orders, _ = await self.sale_orders_repo.get_by_date_range(
            month_start, now
        )
        monthly_sales = sum(
            order.total.amount for order in monthly_orders
        )

        _, total_products = await self.products_repo.get_all(page=1, per_page=1)
        _, total_customers = await self.customers_repo.get_all(page=1, per_page=1)

        low_stock_items_list, low_stock_count = await self.products_repo.get_low_stock(
            page=1, per_page=1
        )

        all_orders, _ = await self.sale_orders_repo.get_all(page=1, per_page=10000)
        pending_orders = sum(
            1
            for o in all_orders
            if o.status in (OrderStatus.DRAFT, OrderStatus.CONFIRMED)
        )

        monthly_purchase_orders, _ = await self.purchase_orders_repo.get_by_date_range(
            month_start, now
        )
        monthly_purchases = sum(
            order.total.amount for order in monthly_purchase_orders
        )

        net_profit = Decimal(str(monthly_sales)) - Decimal(str(monthly_purchases))

        cashboxes, _ = await self.cashbox_repo.get_all(page=1, per_page=10000)
        cashbox_balance = sum(cb.balance.amount for cb in cashboxes)

        customer_debts_total = await self.customer_debt_repo.get_remaining_total()
        supplier_debts_total = await self.supplier_debt_repo.get_remaining_total()

        invoice_count = len(all_orders)

        recent_orders, _ = await self.sale_orders_repo.get_recent(limit=10)
        recent_activities = [
            {
                "order_number": o.order_number,
                "customer_id": o.customer_id,
                "total": float(o.total.amount),
                "status": o.status.value,
                "created_at": o.created_at.isoformat(),
            }
            for o in recent_orders
        ]

        return {
            "daily_sales": daily_sales,
            "monthly_sales": Decimal(str(monthly_sales)),
            "total_products": total_products,
            "total_customers": total_customers,
            "low_stock_items": low_stock_count,
            "pending_orders": pending_orders,
            "total_purchases": Decimal(str(monthly_purchases)),
            "net_profit": net_profit,
            "cashbox_balance": Decimal(str(cashbox_balance)),
            "customer_debts_total": customer_debts_total,
            "supplier_debts_total": supplier_debts_total,
            "invoice_count": invoice_count,
            "recent_activities": recent_activities,
        }
