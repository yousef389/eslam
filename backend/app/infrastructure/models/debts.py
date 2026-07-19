from datetime import datetime

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.domain.enums import DebtStatus, DebtType, PaymentMethod


class CustomerDebtModel(Base):
    __tablename__ = "customer_debts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(36), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    remaining: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    status: Mapped[str] = mapped_column(String(20), default=DebtStatus.PENDING.value)
    description: Mapped[str | None] = mapped_column(nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class SupplierDebtModel(Base):
    __tablename__ = "supplier_debts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(String(36), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    remaining: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    status: Mapped[str] = mapped_column(String(20), default=DebtStatus.PENDING.value)
    description: Mapped[str | None] = mapped_column(nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class DebtPaymentModel(Base):
    __tablename__ = "debt_payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    debt_id: Mapped[str] = mapped_column(String(36), index=True)
    debt_type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    payment_method: Mapped[str] = mapped_column(String(20), default=PaymentMethod.CASH.value)
    notes: Mapped[str | None] = mapped_column(nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
