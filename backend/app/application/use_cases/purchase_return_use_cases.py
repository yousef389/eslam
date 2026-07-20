from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.domain.entities import PurchaseReturn, PurchaseReturnItem
from app.domain.value_objects import Money


class ListPurchaseReturnsUseCase:
    def __init__(self, purchase_returns_repo):
        self.purchase_returns_repo = purchase_returns_repo

    async def execute(self, page: int = 1, per_page: int = 20) -> Tuple[list, int]:
        return await self.purchase_returns_repo.get_all(page, per_page)


class GetPurchaseReturnUseCase:
    def __init__(self, purchase_returns_repo, purchase_return_items_repo):
        self.purchase_returns_repo = purchase_returns_repo
        self.purchase_return_items_repo = purchase_return_items_repo

    async def execute(self, return_id: str) -> dict:
        purchase_return = await self.purchase_returns_repo.get_by_id(return_id)
        if not purchase_return:
            raise NotFoundException("Purchase return", return_id)

        items, _ = await self.purchase_return_items_repo.get_by_return(return_id)
        return {"return": purchase_return, "items": items}


class CreatePurchaseReturnUseCase:
    def __init__(
        self,
        purchase_returns_repo,
        purchase_return_items_repo,
        purchase_orders_repo,
        purchase_order_items_repo,
        products_repo,
        suppliers_repo,
    ):
        self.purchase_returns_repo = purchase_returns_repo
        self.purchase_return_items_repo = purchase_return_items_repo
        self.purchase_orders_repo = purchase_orders_repo
        self.purchase_order_items_repo = purchase_order_items_repo
        self.products_repo = products_repo
        self.suppliers_repo = suppliers_repo

    async def execute(
        self,
        order_id: str,
        supplier_id: str,
        user_id: str,
        items_data: list,
        reason: str = "",
        notes: Optional[str] = None,
    ) -> PurchaseReturn:
        order = await self.purchase_orders_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Purchase order", order_id)

        supplier = await self.suppliers_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", supplier_id)

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

            if quantity <= 0:
                raise ValidationException("Return quantity must be greater than zero")

            if product.quantity_in_stock < quantity:
                raise ConflictException(
                    f"Insufficient stock for product '{product.name}': "
                    f"available {product.quantity_in_stock}, returning {quantity}"
                )

            item_total = unit_price * quantity

            item = PurchaseReturnItem(
                product_id=product.id,
                quantity=quantity,
                unit_price=Money(amount=unit_price),
                total=Money(amount=item_total),
            )
            items.append(item)
            subtotal += item_total

        tax_amount = Decimal("0")
        total = subtotal + tax_amount

        purchase_return = PurchaseReturn(
            return_number=return_number,
            order_id=order_id,
            supplier_id=supplier_id,
            user_id=user_id,
            status="pending",
            subtotal=Money(amount=subtotal),
            tax_amount=Money(amount=tax_amount),
            total=Money(amount=total),
            reason=reason,
            notes=notes or "",
        )

        created_return = await self.purchase_returns_repo.create(purchase_return)

        for item in items:
            item.return_id = created_return.id
            await self.purchase_return_items_repo.create(item)

        for item in items:
            product = await self.products_repo.get_by_id(item.product_id)
            if product:
                product.quantity_in_stock -= item.quantity
                product.updated_at = now
                await self.products_repo.update(product)

        created_return.status = "completed"
        created_return.updated_at = now
        await self.purchase_returns_repo.update(created_return)

        return created_return

    async def _generate_return_number(self, now: datetime) -> str:
        date_part = now.strftime("%Y%m%d")
        returns, total = await self.purchase_returns_repo.get_all(1, 1)
        sequence = total + 1
        return f"PR-{date_part}-{sequence:04d}"
