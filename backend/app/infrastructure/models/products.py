from datetime import datetime

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    barcode: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    category_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    supplier_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    quantity_in_stock: Mapped[int] = mapped_column(default=0)
    minimum_stock_level: Mapped[int] = mapped_column(default=0)
    maximum_stock_level: Mapped[int] = mapped_column(default=1000)
    unit: Mapped[str] = mapped_column(String(20), default="piece")
    is_active: Mapped[bool] = mapped_column(default=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
