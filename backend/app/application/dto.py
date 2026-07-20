from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Auth DTOs ──────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str = "staff"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ── Product DTOs ───────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    sku: str
    barcode: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    unit_price: Decimal
    cost_price: Decimal
    quantity_in_stock: int = 0
    minimum_stock_level: int = 0
    maximum_stock_level: int = 1000
    unit: str = "piece"
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    unit_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    quantity_in_stock: Optional[int] = None
    minimum_stock_level: Optional[int] = None
    maximum_stock_level: Optional[int] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    sku: str
    barcode: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    unit_price: Decimal
    cost_price: Decimal
    quantity_in_stock: int
    minimum_stock_level: int
    maximum_stock_level: int
    unit: str
    is_active: bool
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ── Category DTOs ──────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: bool


# ── Customer DTOs ──────────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    credit_limit: Decimal = Decimal("0")
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    credit_limit: Decimal
    current_balance: Decimal
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ── Supplier DTOs ──────────────────────────────────────────────────────────────

class SupplierCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    payment_terms_days: int = 30
    notes: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    payment_terms_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    payment_terms_days: int
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ── Sale Order DTOs ────────────────────────────────────────────────────────────

class SaleOrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")


class SaleOrderCreate(BaseModel):
    customer_id: str
    items: List[SaleOrderItemCreate]
    discount: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0.14")
    payment_method: str = "cash"
    notes: Optional[str] = None


class SaleOrderItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    discount: Decimal
    total: Decimal


class SaleOrderResponse(BaseModel):
    id: str
    order_number: str
    customer_id: str
    user_id: str
    status: str
    subtotal: Decimal
    discount: Decimal
    tax_amount: Decimal
    total: Decimal
    payment_method: str
    notes: Optional[str] = None
    items: List[SaleOrderItemResponse] = []
    created_at: datetime
    updated_at: datetime


# ── Purchase Order DTOs ────────────────────────────────────────────────────────

class PurchaseOrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    unit_price: Decimal
    discount: Decimal = Decimal("0")


class PurchaseOrderCreate(BaseModel):
    supplier_id: str
    items: List[PurchaseOrderItemCreate]
    discount: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0.14")
    payment_method: str = "cash"
    notes: Optional[str] = None


class PurchaseOrderItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    discount: Decimal
    total: Decimal


class PurchaseOrderResponse(BaseModel):
    id: str
    order_number: str
    supplier_id: str
    user_id: str
    status: str
    subtotal: Decimal
    discount: Decimal
    tax_amount: Decimal
    total: Decimal
    payment_method: str
    notes: Optional[str] = None
    items: List[PurchaseOrderItemResponse] = []
    created_at: datetime
    updated_at: datetime


# ── Purchase Return DTOs ──────────────────────────────────────────────────────

class PurchaseReturnItemCreate(BaseModel):
    product_id: str
    quantity: int
    unit_price: Decimal


class PurchaseReturnCreate(BaseModel):
    order_id: str
    supplier_id: str
    items: List[PurchaseReturnItemCreate]
    reason: Optional[str] = None
    notes: Optional[str] = None


class PurchaseReturnItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    total: Decimal


class PurchaseReturnResponse(BaseModel):
    id: str
    return_number: str
    order_id: str
    supplier_id: str
    user_id: str
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    reason: Optional[str] = None
    notes: Optional[str] = None
    items: List[PurchaseReturnItemResponse] = []
    created_at: datetime
    updated_at: datetime


# ── Dashboard DTOs ─────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    daily_sales: Decimal = Decimal("0")
    monthly_sales: Decimal = Decimal("0")
    total_products: int = 0
    total_customers: int = 0
    low_stock_items: int = 0
    pending_orders: int = 0
    total_purchases: Decimal = Decimal("0")
    net_profit: Decimal = Decimal("0")
    cashbox_balance: Decimal = Decimal("0")
    customer_debts_total: Decimal = Decimal("0")
    supplier_debts_total: Decimal = Decimal("0")
    invoice_count: int = 0
    recent_activities: list = []


# ── Accounting DTOs ────────────────────────────────────────────────────────────

class DebtCreate(BaseModel):
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    amount: Decimal
    description: str
    due_date: Optional[datetime] = None


class DebtPaymentCreate(BaseModel):
    debt_id: str
    amount: Decimal
    payment_method: str = "cash"
    notes: Optional[str] = None


class DebtResponse(BaseModel):
    id: str
    amount: Decimal
    paid_amount: Decimal
    remaining: Decimal
    status: str
    description: str
    due_date: Optional[datetime] = None
    created_at: datetime


class CashboxResponse(BaseModel):
    id: str
    name: str
    balance: Decimal
    is_active: bool


class CashboxTransactionCreate(BaseModel):
    cashbox_id: str
    amount: Decimal
    transaction_type: str
    description: str
    reference_id: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    transaction_number: str
    type: str
    amount: Decimal
    description: str
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    user_id: str
    created_at: datetime


# ── Reports DTOs ───────────────────────────────────────────────────────────────

class ReportSummary(BaseModel):
    total_sales: Decimal
    total_purchases: Decimal
    net_profit: Decimal
    total_receivable: Decimal
    total_payable: Decimal
    transaction_count: int


# ── Pagination DTOs ────────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20
    search: Optional[str] = None


class PaginatedResponse(BaseModel):
    data: list
    meta: dict


# ── Extraction DTOs ────────────────────────────────────────────────────────────

class ExtractionCreate(BaseModel):
    image_url: Optional[str] = None
    source: str = "api"
    raw_text: Optional[str] = None


class ExtractionResponse(BaseModel):
    id: str
    image_url: Optional[str] = None
    source: str
    status: str
    raw_text: Optional[str] = None
    extracted_data: Optional[dict] = None
    review_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExtractionReview(BaseModel):
    status: str
    review_notes: Optional[str] = None
