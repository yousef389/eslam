from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.domain.entities import Product
from app.domain.value_objects import Money


class ListProductsUseCase:
    def __init__(self, products_repo):
        self.products_repo = products_repo

    async def execute(
        self, page: int = 1, per_page: int = 20, search: Optional[str] = None
    ) -> Tuple[list, int]:
        if search:
            return await self.products_repo.search(search, page, per_page)
        return await self.products_repo.get_all(page, per_page)


class GetProductUseCase:
    def __init__(self, products_repo):
        self.products_repo = products_repo

    async def execute(self, product_id: str) -> Product:
        product = await self.products_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product


class CreateProductUseCase:
    def __init__(self, products_repo):
        self.products_repo = products_repo

    async def execute(
        self,
        name: str,
        sku: str,
        unit_price: Decimal,
        cost_price: Decimal,
        quantity_in_stock: int = 0,
        minimum_stock_level: int = 0,
        maximum_stock_level: int = 1000,
        unit: str = "piece",
        barcode: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Product:
        existing = await self.products_repo.get_by_sku(sku)
        if existing:
            raise ConflictException(f"Product with SKU '{sku}' already exists")

        if barcode:
            existing_barcode = await self.products_repo.get_by_barcode(barcode)
            if existing_barcode:
                raise ConflictException(f"Product with barcode '{barcode}' already exists")

        if unit_price < 0 or cost_price < 0:
            raise ValidationException("Prices cannot be negative")

        if quantity_in_stock < 0:
            raise ValidationException("Stock quantity cannot be negative")

        product = Product(
            name=name,
            sku=sku,
            barcode=barcode or "",
            description=description or "",
            category_id=category_id,
            unit_price=Money(amount=unit_price),
            cost_price=Money(amount=cost_price),
            quantity_in_stock=quantity_in_stock,
            minimum_stock_level=minimum_stock_level,
            maximum_stock_level=maximum_stock_level,
            unit=unit,
            image_url=image_url,
        )

        return await self.products_repo.create(product)


class UpdateProductUseCase:
    def __init__(self, products_repo):
        self.products_repo = products_repo

    async def execute(self, product_id: str, updates: dict) -> Product:
        product = await self.products_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)

        if "sku" in updates and updates["sku"] is not None:
            existing = await self.products_repo.get_by_sku(updates["sku"])
            if existing and existing.id != product_id:
                raise ConflictException(f"SKU '{updates['sku']}' already in use")

        if "barcode" in updates and updates["barcode"]:
            existing = await self.products_repo.get_by_barcode(updates["barcode"])
            if existing and existing.id != product_id:
                raise ConflictException(f"Barcode already in use")

        if "unit_price" in updates and updates["unit_price"] is not None:
            product.unit_price = Money(amount=updates["unit_price"])
        if "cost_price" in updates and updates["cost_price"] is not None:
            product.cost_price = Money(amount=updates["cost_price"])

        for field in [
            "name", "sku", "barcode", "description", "category_id",
            "quantity_in_stock", "minimum_stock_level", "maximum_stock_level",
            "unit", "image_url", "is_active",
        ]:
            if field in updates and updates[field] is not None:
                setattr(product, field, updates[field])

        product.updated_at = datetime.utcnow()
        return await self.products_repo.update(product)


class DeleteProductUseCase:
    def __init__(self, products_repo):
        self.products_repo = products_repo

    async def execute(self, product_id: str) -> None:
        product = await self.products_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)

        product.is_active = False
        product.updated_at = datetime.utcnow()
        await self.products_repo.update(product)


class GetLowStockProductsUseCase:
    def __init__(self, products_repo):
        self.products_repo = products_repo

    async def execute(
        self, page: int = 1, per_page: int = 20
    ) -> Tuple[list, int]:
        return await self.products_repo.get_low_stock(page, per_page)
