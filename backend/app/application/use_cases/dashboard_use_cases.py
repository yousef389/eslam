from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.domain.enums import OrderStatus


class GetDashboardStatsUseCase:
    def __init__(
        self,
        sale_orders_repo,
        purchase_orders_repo,
        products_repo,
        customers_repo,
    ):
        self.sale_orders_repo = sale_orders_repo
        self.purchase_orders_repo = purchase_orders_repo
        self.products_repo = products_repo
        self.customers_repo = customers_repo

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

        return {
            "daily_sales": daily_sales,
            "monthly_sales": Decimal(str(monthly_sales)),
            "total_products": total_products,
            "total_customers": total_customers,
            "low_stock_items": low_stock_count,
            "pending_orders": pending_orders,
        }
