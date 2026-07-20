from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.domain.entities import SaleOrder, SaleOrderItem
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.value_objects import Money


class ListSaleOrdersUseCase:
    def __init__(self, sale_orders_repo):
        self.sale_orders_repo = sale_orders_repo

    async def execute(
        self,
        page: int = 1,
        per_page: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[list, int]:
        if start_date and end_date:
            return await self.sale_orders_repo.get_by_date_range(
                start_date, end_date, page, per_page
            )
        return await self.sale_orders_repo.get_all(page, per_page)


class GetSaleOrderUseCase:
    def __init__(self, sale_orders_repo, sale_order_items_repo):
        self.sale_orders_repo = sale_orders_repo
        self.sale_order_items_repo = sale_order_items_repo

    async def execute(self, order_id: str) -> dict:
        order = await self.sale_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Sale order", order_id)

        items, _ = await self.sale_order_items_repo.get_by_order(order_id)
        return {"order": order, "items": items}


class CreateSaleOrderUseCase:
    def __init__(
        self,
        sale_orders_repo,
        sale_order_items_repo,
        products_repo,
        customers_repo,
    ):
        self.sale_orders_repo = sale_orders_repo
        self.sale_order_items_repo = sale_order_items_repo
        self.products_repo = products_repo
        self.customers_repo = customers_repo

    async def execute(
        self,
        customer_id: str,
        user_id: str,
        items_data: list,
        discount: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0.14"),
        payment_method: str = "cash",
        notes: Optional[str] = None,
    ) -> SaleOrder:
        customer = await self.customers_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)

        if not customer.is_active:
            raise ValidationException("Customer account is inactive")

        if not items_data:
            raise ValidationException("Order must have at least one item")

        now = datetime.utcnow()
        order_number = await self._generate_order_number(now)

        try:
            pay_method = PaymentMethod(payment_method)
        except ValueError:
            raise ValidationException(f"Invalid payment method: {payment_method}")

        subtotal = Decimal("0")
        items = []

        for item_data in items_data:
            product = await self.products_repo.get_by_id(item_data["product_id"])
            if not product:
                raise NotFoundException("Product", item_data["product_id"])

            if not product.is_active:
                raise ValidationException(
                    f"Product '{product.name}' is inactive"
                )

            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]
            item_discount = item_data.get("discount", Decimal("0"))

            item_total = (unit_price * quantity) - item_discount

            item = SaleOrderItem(
                product_id=product.id,
                quantity=quantity,
                unit_price=Money(amount=unit_price),
                discount=Money(amount=item_discount),
                total=Money(amount=item_total),
            )
            items.append(item)
            subtotal += item_total

        tax_amount = subtotal * tax_rate
        total = subtotal - discount + tax_amount

        order = SaleOrder(
            order_number=order_number,
            customer_id=customer_id,
            user_id=user_id,
            status=OrderStatus.CONFIRMED,
            subtotal=Money(amount=subtotal),
            discount=Money(amount=discount),
            tax_amount=Money(amount=tax_amount),
            total=Money(amount=total),
            payment_method=pay_method,
            notes=notes or "",
        )

        created_order = await self.sale_orders_repo.create(order)

        for item in items:
            item.order_id = created_order.id
            created_item = await self.sale_order_items_repo.create(item)

            product = await self.products_repo.get_by_id(item.product_id)
            if product.quantity_in_stock < item.quantity:
                raise ValidationException(
                    f"Insufficient stock for product '{product.name}'"
                )
            product.quantity_in_stock -= item.quantity
            product.updated_at = now
            await self.products_repo.update(product)

        return created_order

    async def _generate_order_number(self, now: datetime) -> str:
        date_part = now.strftime("%Y%m%d")
        orders, total = await self.sale_orders_repo.get_by_date_range(
            now.replace(hour=0, minute=0, second=0, microsecond=0),
            now.replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        sequence = total + 1
        return f"SO-{date_part}-{sequence:04d}"


class UpdateSaleOrderStatusUseCase:
    def __init__(self, sale_orders_repo):
        self.sale_orders_repo = sale_orders_repo

    async def execute(self, order_id: str, status: str) -> SaleOrder:
        order = await self.sale_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Sale order", order_id)

        try:
            new_status = OrderStatus(status)
        except ValueError:
            raise ValidationException(f"Invalid status: {status}")

        valid_transitions = {
            OrderStatus.DRAFT: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }

        allowed = valid_transitions.get(order.status, [])
        if new_status not in allowed:
            raise ConflictException(
                f"Cannot transition from '{order.status.value}' to '{new_status.value}'"
            )

        order.status = new_status
        order.updated_at = datetime.utcnow()
        return await self.sale_orders_repo.update(order)


class DeleteSaleOrderUseCase:
    def __init__(self, sale_orders_repo, sale_order_items_repo, products_repo):
        self.sale_orders_repo = sale_orders_repo
        self.sale_order_items_repo = sale_order_items_repo
        self.products_repo = products_repo

    async def execute(self, order_id: str) -> None:
        order = await self.sale_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Sale order", order_id)

        items, _ = await self.sale_order_items_repo.get_by_order(order_id)

        for item in items:
            product = await self.products_repo.get_by_id(item.product_id)
            if product:
                product.quantity_in_stock += item.quantity
                product.updated_at = datetime.utcnow()
                await self.products_repo.update(product)

        for item in items:
            await self.sale_order_items_repo.delete(item.id)

        await self.sale_orders_repo.delete(order_id)
