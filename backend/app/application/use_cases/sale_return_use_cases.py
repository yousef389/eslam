from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import NotFoundException, ValidationException
from app.domain.entities import SaleReturn, SaleReturnItem
from app.domain.enums import OrderStatus
from app.domain.value_objects import Money


class ListSaleReturnsUseCase:
    def __init__(self, sale_returns_repo):
        self.sale_returns_repo = sale_returns_repo

    async def execute(self, page: int = 1, per_page: int = 20) -> Tuple[list, int]:
        return await self.sale_returns_repo.get_all(page, per_page)


class GetSaleReturnUseCase:
    def __init__(self, sale_returns_repo, sale_return_items_repo):
        self.sale_returns_repo = sale_returns_repo
        self.sale_return_items_repo = sale_return_items_repo

    async def execute(self, return_id: str) -> dict:
        sale_return = await self.sale_returns_repo.get_by_id(return_id)
        if not sale_return:
            raise NotFoundException("Sale return", return_id)

        items, _ = await self.sale_return_items_repo.get_by_return(return_id)
        return {"sale_return": sale_return, "items": items}


class CreateSaleReturnUseCase:
    def __init__(
        self,
        sale_returns_repo,
        sale_return_items_repo,
        sale_orders_repo,
        products_repo,
    ):
        self.sale_returns_repo = sale_returns_repo
        self.sale_return_items_repo = sale_return_items_repo
        self.sale_orders_repo = sale_orders_repo
        self.products_repo = products_repo

    async def execute(
        self,
        order_id: str,
        user_id: str,
        items_data: list,
        reason: str = "",
        notes: str = "",
    ) -> SaleReturn:
        order = await self.sale_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Sale order", order_id)

        if not items_data:
            raise ValidationException("Return must have at least one item")

        now = datetime.utcnow()
        return_number = await self._generate_return_number(now)

        subtotal = Decimal("0")
        items = []

        for item_data in items_data:
            product = await self.products_repo.get_by_id(item_data["product_id"])
            if not product:
                raise NotFoundException("Product", item_data["product_id"])

            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]

            item_total = unit_price * quantity

            item = SaleReturnItem(
                product_id=product.id,
                quantity=quantity,
                unit_price=Money(amount=unit_price),
                total=Money(amount=item_total),
            )
            items.append(item)
            subtotal += item_total

            product.quantity_in_stock += quantity
            product.updated_at = now
            await self.products_repo.update(product)

        tax_amount = subtotal * Decimal("0.14")
        total = subtotal + tax_amount

        sale_return = SaleReturn(
            return_number=return_number,
            order_id=order_id,
            customer_id=order.customer_id,
            user_id=user_id,
            status="completed",
            subtotal=Money(amount=subtotal),
            tax_amount=Money(amount=tax_amount),
            total=Money(amount=total),
            reason=reason,
            notes=notes,
        )

        created_return = await self.sale_returns_repo.create(sale_return)

        for item in items:
            item.return_id = created_return.id
            await self.sale_return_items_repo.create(item)

        order.status = OrderStatus.RETURNED
        order.updated_at = now
        await self.sale_orders_repo.update(order)

        return created_return

    async def _generate_return_number(self, now: datetime) -> str:
        date_part = now.strftime("%Y%m%d")
        returns, total = await self.sale_returns_repo.get_all(page=1, per_page=10000)
        sequence = total + 1
        return f"SR-{date_part}-{sequence:04d}"
