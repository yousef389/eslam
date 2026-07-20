from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.domain.entities import PurchaseOrder, PurchaseOrderItem
from app.domain.enums import OrderStatus, PaymentMethod
from app.domain.value_objects import Money


class ListPurchaseOrdersUseCase:
    def __init__(self, purchase_orders_repo):
        self.purchase_orders_repo = purchase_orders_repo

    async def execute(
        self,
        page: int = 1,
        per_page: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[list, int]:
        if start_date and end_date:
            return await self.purchase_orders_repo.get_by_date_range(
                start_date, end_date, page, per_page
            )
        return await self.purchase_orders_repo.get_all(page, per_page)


class SearchPurchaseOrdersUseCase:
    def __init__(self, purchase_orders_repo):
        self.purchase_orders_repo = purchase_orders_repo

    async def execute(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[list, int]:
        return await self.purchase_orders_repo.search(query, page, per_page)


class GetPurchaseOrderUseCase:
    def __init__(self, purchase_orders_repo, purchase_order_items_repo):
        self.purchase_orders_repo = purchase_orders_repo
        self.purchase_order_items_repo = purchase_order_items_repo

    async def execute(self, order_id: str) -> dict:
        order = await self.purchase_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Purchase order", order_id)

        items, _ = await self.purchase_order_items_repo.get_by_order(order_id)
        return {"order": order, "items": items}


class CreatePurchaseOrderUseCase:
    def __init__(
        self,
        purchase_orders_repo,
        purchase_order_items_repo,
        products_repo,
        suppliers_repo,
    ):
        self.purchase_orders_repo = purchase_orders_repo
        self.purchase_order_items_repo = purchase_order_items_repo
        self.products_repo = products_repo
        self.suppliers_repo = suppliers_repo

    async def execute(
        self,
        supplier_id: str,
        user_id: str,
        items_data: list,
        discount: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0.14"),
        payment_method: str = "cash",
        notes: Optional[str] = None,
    ) -> PurchaseOrder:
        supplier = await self.suppliers_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", supplier_id)

        if not supplier.is_active:
            raise ValidationException("Supplier account is inactive")

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

            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]
            item_discount = item_data.get("discount", Decimal("0"))

            item_total = (unit_price * quantity) - item_discount

            item = PurchaseOrderItem(
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

        order = PurchaseOrder(
            order_number=order_number,
            supplier_id=supplier_id,
            user_id=user_id,
            status=OrderStatus.CONFIRMED,
            subtotal=Money(amount=subtotal),
            discount=Money(amount=discount),
            tax_amount=Money(amount=tax_amount),
            total=Money(amount=total),
            payment_method=pay_method,
            notes=notes or "",
        )

        created_order = await self.purchase_orders_repo.create(order)

        for item in items:
            item.order_id = created_order.id
            await self.purchase_order_items_repo.create(item)

        return created_order

    async def _generate_order_number(self, now: datetime) -> str:
        date_part = now.strftime("%Y%m%d")
        orders, total = await self.purchase_orders_repo.get_by_date_range(
            now.replace(hour=0, minute=0, second=0, microsecond=0),
            now.replace(hour=23, minute=59, second=59, microsecond=999999),
        )
        sequence = total + 1
        return f"PO-{date_part}-{sequence:04d}"


class UpdatePurchaseOrderStatusUseCase:
    def __init__(self, purchase_orders_repo, products_repo):
        self.purchase_orders_repo = purchase_orders_repo
        self.products_repo = products_repo

    async def execute(
        self,
        order_id: str,
        status: str,
        purchase_order_items_repo=None,
    ) -> PurchaseOrder:
        order = await self.purchase_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Purchase order", order_id)

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

        if (
            new_status == OrderStatus.DELIVERED
            and order.status == OrderStatus.SHIPPED
            and purchase_order_items_repo
        ):
            items, _ = await purchase_order_items_repo.get_by_order(order_id)
            now = datetime.utcnow()
            for item in items:
                product = await self.products_repo.get_by_id(item.product_id)
                if product:
                    product.quantity_in_stock += item.quantity
                    product.updated_at = now
                    await self.products_repo.update(product)

        order.status = new_status
        order.updated_at = datetime.utcnow()
        return await self.purchase_orders_repo.update(order)


class DeletePurchaseOrderUseCase:
    def __init__(self, purchase_orders_repo, purchase_order_items_repo, products_repo):
        self.purchase_orders_repo = purchase_orders_repo
        self.purchase_order_items_repo = purchase_order_items_repo
        self.products_repo = products_repo

    async def execute(self, order_id: str) -> None:
        order = await self.purchase_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Purchase order", order_id)

        items, _ = await self.purchase_order_items_repo.get_by_order(order_id)

        if order.status == OrderStatus.DELIVERED:
            now = datetime.utcnow()
            for item in items:
                product = await self.products_repo.get_by_id(item.product_id)
                if product:
                    product.quantity_in_stock -= item.quantity
                    product.updated_at = now
                    await self.products_repo.update(product)

        for item in items:
            await self.purchase_order_items_repo.delete(item.id)

        await self.purchase_orders_repo.delete(order_id)
