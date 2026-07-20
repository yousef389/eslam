from datetime import datetime

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class SaleReturnModel(Base):
    __tablename__ = "sale_returns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    return_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    order_id: Mapped[str] = mapped_column(String(36), index=True)
    customer_id: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    reason: Mapped[str | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class SaleReturnItemModel(Base):
    __tablename__ = "sale_return_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    return_id: Mapped[str] = mapped_column(String(36), index=True)
    product_id: Mapped[str] = mapped_column(String(36), index=True)
    quantity: Mapped[int] = mapped_column(default=0)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
