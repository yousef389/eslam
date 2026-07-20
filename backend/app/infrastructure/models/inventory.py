from datetime import datetime

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class WarehouseModel(Base):
    __tablename__ = "warehouses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class WarehouseStockModel(Base):
    __tablename__ = "warehouse_stocks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    warehouse_id: Mapped[str] = mapped_column(String(36), index=True)
    product_id: Mapped[str] = mapped_column(String(36), index=True)
    quantity: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class StockMovementModel(Base):
    __tablename__ = "stock_movements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    movement_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    product_id: Mapped[str] = mapped_column(String(36), index=True)
    warehouse_id: Mapped[str] = mapped_column(String(36), index=True)
    movement_type: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[int] = mapped_column(default=0)
    reference_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class StockTransferModel(Base):
    __tablename__ = "stock_transfers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    transfer_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    product_id: Mapped[str] = mapped_column(String(36), index=True)
    from_warehouse_id: Mapped[str] = mapped_column(String(36), index=True)
    to_warehouse_id: Mapped[str] = mapped_column(String(36), index=True)
    quantity: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class CashboxTransferModel(Base):
    __tablename__ = "cashbox_transfers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    transfer_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    from_cashbox_id: Mapped[str] = mapped_column(String(36), index=True)
    to_cashbox_id: Mapped[str] = mapped_column(String(36), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
