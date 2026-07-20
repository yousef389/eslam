from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from .enums import (
    DebtStatus,
    DebtType,
    ExtractionStatus,
    OrderStatus,
    PaymentMethod,
    SettingsGroup,
    StockMovementType,
    TransactionType,
    UserRole,
)
from .value_objects import Address, Money


def _now_utc() -> datetime:
    return datetime.utcnow()


def _new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class User:
    id: str = field(default_factory=_new_id)
    username: str = ""
    email: str = ""
    full_name: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.STAFF
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class Category:
    id: str = field(default_factory=_new_id)
    name: str = ""
    description: str = ""
    parent_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class Product:
    id: str = field(default_factory=_new_id)
    name: str = ""
    sku: str = ""
    barcode: str = ""
    description: str = ""
    category_id: Optional[str] = None
    supplier_id: Optional[str] = None
    unit_price: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    cost_price: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    quantity_in_stock: int = 0
    minimum_stock_level: int = 0
    maximum_stock_level: int = 0
    unit: str = "piece"
    is_active: bool = True
    image_url: Optional[str] = None
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class Customer:
    id: str = field(default_factory=_new_id)
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    address: Optional[Address] = None
    tax_number: Optional[str] = None
    credit_limit: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    current_balance: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    is_active: bool = True
    notes: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class Supplier:
    id: str = field(default_factory=_new_id)
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    address: Optional[Address] = None
    tax_number: Optional[str] = None
    payment_terms_days: int = 30
    is_active: bool = True
    notes: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class SaleOrderItem:
    id: str = field(default_factory=_new_id)
    order_id: str = ""
    product_id: str = ""
    quantity: int = 0
    unit_price: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    discount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class SaleOrder:
    id: str = field(default_factory=_new_id)
    order_number: str = ""
    customer_id: str = ""
    user_id: str = ""
    status: OrderStatus = OrderStatus.DRAFT
    subtotal: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    discount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    tax_amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    payment_method: Optional[PaymentMethod] = None
    notes: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class PurchaseOrderItem:
    id: str = field(default_factory=_new_id)
    order_id: str = ""
    product_id: str = ""
    quantity: int = 0
    unit_price: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    discount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class PurchaseOrder:
    id: str = field(default_factory=_new_id)
    order_number: str = ""
    supplier_id: str = ""
    user_id: str = ""
    status: OrderStatus = OrderStatus.DRAFT
    subtotal: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    discount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    tax_amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    payment_method: Optional[PaymentMethod] = None
    notes: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class PurchaseReturn:
    id: str = field(default_factory=_new_id)
    return_number: str = ""
    order_id: str = ""
    supplier_id: str = ""
    user_id: str = ""
    status: str = "pending"
    subtotal: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    tax_amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    reason: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class PurchaseReturnItem:
    id: str = field(default_factory=_new_id)
    return_id: str = ""
    product_id: str = ""
    quantity: int = 0
    unit_price: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    created_at: datetime = field(default_factory=_now_utc)


@dataclass
class SaleReturn:
    id: str = field(default_factory=_new_id)
    return_number: str = ""
    order_id: str = ""
    customer_id: str = ""
    user_id: str = ""
    status: str = "pending"
    subtotal: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    tax_amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    reason: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class SaleReturnItem:
    id: str = field(default_factory=_new_id)
    return_id: str = ""
    product_id: str = ""
    quantity: int = 0
    unit_price: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    total: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    created_at: datetime = field(default_factory=_now_utc)


@dataclass
class Transaction:
    id: str = field(default_factory=_new_id)
    transaction_number: str = ""
    type: TransactionType = TransactionType.INCOME
    amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    description: str = ""
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    user_id: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class CustomerDebt:
    id: str = field(default_factory=_new_id)
    customer_id: str = ""
    amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    paid_amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    remaining: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    status: DebtStatus = DebtStatus.PENDING
    description: str = ""
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class SupplierDebt:
    id: str = field(default_factory=_new_id)
    supplier_id: str = ""
    amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    paid_amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    remaining: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    status: DebtStatus = DebtStatus.PENDING
    description: str = ""
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class DebtPayment:
    id: str = field(default_factory=_new_id)
    debt_id: str = ""
    debt_type: DebtType = DebtType.CUSTOMER
    amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    payment_method: PaymentMethod = PaymentMethod.CASH
    notes: str = ""
    user_id: str = ""
    created_at: datetime = field(default_factory=_now_utc)


@dataclass
class Cashbox:
    id: str = field(default_factory=_new_id)
    name: str = ""
    balance: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    is_active: bool = True
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class CashboxTransaction:
    id: str = field(default_factory=_new_id)
    cashbox_id: str = ""
    transaction_type: TransactionType = TransactionType.INCOME
    amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    description: str = ""
    reference_id: Optional[str] = None
    user_id: str = ""
    created_at: datetime = field(default_factory=_now_utc)


@dataclass
class Extraction:
    id: str = field(default_factory=_new_id)
    image_url: str = ""
    source: str = "api"
    status: ExtractionStatus = ExtractionStatus.PENDING
    raw_text: str = ""
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    review_notes: str = ""
    reviewed_by: Optional[str] = None
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class AuditLog:
    id: str = field(default_factory=_new_id)
    user_id: str = ""
    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    created_at: datetime = field(default_factory=_now_utc)


@dataclass
class SystemSetting:
    id: str = field(default_factory=_new_id)
    key: str = ""
    value: str = ""
    group: SettingsGroup = SettingsGroup.STORE
    description: str = ""
    is_secret: bool = False
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class Warehouse:
    id: str = field(default_factory=_new_id)
    name: str = ""
    location: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class WarehouseStock:
    id: str = field(default_factory=_new_id)
    warehouse_id: str = ""
    product_id: str = ""
    quantity: int = 0
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class StockMovement:
    id: str = field(default_factory=_new_id)
    movement_number: str = ""
    product_id: str = ""
    warehouse_id: str = ""
    movement_type: StockMovementType = StockMovementType.PURCHASE
    quantity: int = 0
    reference_id: Optional[str] = None
    notes: str = ""
    user_id: str = ""
    created_at: datetime = field(default_factory=_now_utc)


@dataclass
class StockTransfer:
    id: str = field(default_factory=_new_id)
    transfer_number: str = ""
    product_id: str = ""
    from_warehouse_id: str = ""
    to_warehouse_id: str = ""
    quantity: int = 0
    status: str = "pending"
    notes: str = ""
    user_id: str = ""
    created_at: datetime = field(default_factory=_now_utc)
    updated_at: datetime = field(default_factory=_now_utc)


@dataclass
class CashboxTransfer:
    id: str = field(default_factory=_new_id)
    transfer_number: str = ""
    from_cashbox_id: str = ""
    to_cashbox_id: str = ""
    amount: Money = field(default_factory=lambda: Money(amount=Decimal("0.00")))
    description: str = ""
    user_id: str = ""
    created_at: datetime = field(default_factory=_now_utc)
