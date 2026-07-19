from datetime import datetime

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.domain.enums import TransactionType


class CashboxModel(Base):
    __tablename__ = "cashboxes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class CashboxTransactionModel(Base):
    __tablename__ = "cashbox_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cashbox_id: Mapped[str] = mapped_column(String(36), index=True)
    transaction_type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    description: Mapped[str] = mapped_column(String(255))
    reference_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
