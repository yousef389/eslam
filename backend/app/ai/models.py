from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class ExtractedProduct(BaseModel):
    name: str
    sku: Optional[str] = None
    quantity: int = 0
    unit_price: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    unit: str = "piece"
    confidence: float = 0.0


class ExtractedCustomer(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    confidence: float = 0.0


class ExtractedPrice(BaseModel):
    product_name: str
    price: Decimal
    currency: str = "EGP"
    confidence: float = 0.0


class ExtractedDebtEntry(BaseModel):
    customer_name: str
    amount: Decimal
    description: str = ""
    date: Optional[datetime] = None
    confidence: float = 0.0


class ExtractedInvoice(BaseModel):
    invoice_number: Optional[str] = None
    date: Optional[datetime] = None
    customer: Optional[ExtractedCustomer] = None
    supplier: Optional[ExtractedCustomer] = None
    products: List[ExtractedProduct] = []
    subtotal: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    payment_method: Optional[str] = None
    confidence: float = 0.0


class ExtractionResult(BaseModel):
    source_type: str  # "invoice", "product_list", "price_list", "debt_ledger", "text"
    raw_text: Optional[str] = None
    invoice: Optional[ExtractedInvoice] = None
    products: List[ExtractedProduct] = []
    prices: List[ExtractedPrice] = []
    debt_entries: List[ExtractedDebtEntry] = []
    confidence: float = 0.0
    notes: Optional[str] = None
