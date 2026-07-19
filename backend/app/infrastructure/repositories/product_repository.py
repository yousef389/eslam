from decimal import Decimal
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Product
from app.domain.repositories import ProductRepository
from app.domain.value_objects import Money
from app.infrastructure.models.products import ProductModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: ProductModel) -> Product:
    return Product(
        id=model.id,
        name=model.name,
        sku=model.sku,
        barcode=model.barcode or "",
        description=model.description or "",
        category_id=model.category_id,
        unit_price=Money(amount=Decimal(str(model.unit_price))),
        cost_price=Money(amount=Decimal(str(model.cost_price))),
        quantity_in_stock=model.quantity_in_stock,
        minimum_stock_level=model.minimum_stock_level,
        maximum_stock_level=model.maximum_stock_level,
        unit=model.unit,
        is_active=model.is_active,
        image_url=model.image_url,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: Product) -> ProductModel:
    return ProductModel(
        id=entity.id,
        name=entity.name,
        sku=entity.sku,
        barcode=entity.barcode or None,
        description=entity.description or None,
        category_id=entity.category_id,
        unit_price=float(entity.unit_price.amount),
        cost_price=float(entity.cost_price.amount),
        quantity_in_stock=entity.quantity_in_stock,
        minimum_stock_level=entity.minimum_stock_level,
        maximum_stock_level=entity.maximum_stock_level,
        unit=entity.unit,
        is_active=entity.is_active,
        image_url=entity.image_url,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class ProductRepositoryImpl(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, ProductModel)

    async def get_by_id(self, id: str) -> Optional[Product]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Product], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: Product) -> Product:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: Product) -> Product:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.name = entity.name
            model.sku = entity.sku
            model.barcode = entity.barcode or None
            model.description = entity.description or None
            model.category_id = entity.category_id
            model.unit_price = float(entity.unit_price.amount)
            model.cost_price = float(entity.cost_price.amount)
            model.quantity_in_stock = entity.quantity_in_stock
            model.minimum_stock_level = entity.minimum_stock_level
            model.maximum_stock_level = entity.maximum_stock_level
            model.unit = entity.unit
            model.is_active = entity.is_active
            model.image_url = entity.image_url
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        stmt = select(ProductModel).where(ProductModel.sku == sku)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None

    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        stmt = select(ProductModel).where(ProductModel.barcode == barcode)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None

    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[Product], int]:
        pattern = f"%{query}%"
        base_filter = (
            ProductModel.name.ilike(pattern) | ProductModel.sku.ilike(pattern)
        )

        count_stmt = select(func.count()).select_from(ProductModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(ProductModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_low_stock(self, page: int = 1, per_page: int = 20) -> Tuple[List[Product], int]:
        from sqlalchemy import cast, Integer
        base_filter = ProductModel.quantity_in_stock <= ProductModel.minimum_stock_level

        count_stmt = select(func.count()).select_from(ProductModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(ProductModel)
            .where(base_filter)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
