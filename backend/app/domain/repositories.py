from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Generic, List, Optional, Tuple, TypeVar

from .entities import (
    AuditLog,
    Cashbox,
    CashboxTransaction,
    Category,
    Customer,
    CustomerDebt,
    DebtPayment,
    Extraction,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    SaleOrder,
    SaleOrderItem,
    Supplier,
    SupplierDebt,
    Transaction,
    User,
)
from .enums import DebtStatus, ExtractionStatus, TransactionType

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[T], int]:
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        ...

    @abstractmethod
    async def update(self, entity: T) -> T:
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        ...


class UserRepository(BaseRepository[User]):
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        ...


class ProductRepository(BaseRepository[Product]):
    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        ...

    @abstractmethod
    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        ...

    @abstractmethod
    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[Product], int]:
        ...

    @abstractmethod
    async def get_low_stock(self, page: int = 1, per_page: int = 20) -> Tuple[List[Product], int]:
        ...


class CategoryRepository(BaseRepository[Category]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        ...


class CustomerRepository(BaseRepository[Customer]):
    @abstractmethod
    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[Customer], int]:
        ...

    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        ...


class SupplierRepository(BaseRepository[Supplier]):
    @abstractmethod
    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[Supplier], int]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Supplier]:
        ...


class SaleOrderRepository(BaseRepository[SaleOrder]):
    @abstractmethod
    async def get_by_order_number(self, order_number: str) -> Optional[SaleOrder]:
        ...

    @abstractmethod
    async def get_by_customer(
        self, customer_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleOrder], int]:
        ...

    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleOrder], int]:
        ...

    @abstractmethod
    async def get_daily_sales(
        self, date: datetime
    ) -> Decimal:
        ...


class SaleOrderItemRepository(BaseRepository[SaleOrderItem]):
    @abstractmethod
    async def get_by_order(
        self, order_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleOrderItem], int]:
        ...


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    @abstractmethod
    async def get_by_order_number(self, order_number: str) -> Optional[PurchaseOrder]:
        ...

    @abstractmethod
    async def get_by_supplier(
        self, supplier_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseOrder], int]:
        ...

    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseOrder], int]:
        ...


class PurchaseOrderItemRepository(BaseRepository[PurchaseOrderItem]):
    @abstractmethod
    async def get_by_order(
        self, order_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseOrderItem], int]:
        ...


class TransactionRepository(BaseRepository[Transaction]):
    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Transaction], int]:
        ...

    @abstractmethod
    async def get_by_type(
        self, tx_type: TransactionType, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Transaction], int]:
        ...

    @abstractmethod
    async def get_summary(
        self, start_date: datetime, end_date: datetime
    ) -> dict:
        ...


class CustomerDebtRepository(BaseRepository[CustomerDebt]):
    @abstractmethod
    async def get_by_customer(
        self, customer_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CustomerDebt], int]:
        ...

    @abstractmethod
    async def get_overdue(self, page: int = 1, per_page: int = 20) -> Tuple[List[CustomerDebt], int]:
        ...

    @abstractmethod
    async def get_pending(self, page: int = 1, per_page: int = 20) -> Tuple[List[CustomerDebt], int]:
        ...


class SupplierDebtRepository(BaseRepository[SupplierDebt]):
    @abstractmethod
    async def get_by_supplier(
        self, supplier_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SupplierDebt], int]:
        ...

    @abstractmethod
    async def get_overdue(self, page: int = 1, per_page: int = 20) -> Tuple[List[SupplierDebt], int]:
        ...

    @abstractmethod
    async def get_pending(self, page: int = 1, per_page: int = 20) -> Tuple[List[SupplierDebt], int]:
        ...


class DebtPaymentRepository(BaseRepository[DebtPayment]):
    @abstractmethod
    async def get_by_debt(
        self, debt_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[DebtPayment], int]:
        ...


class CashboxRepository(BaseRepository[Cashbox]):
    @abstractmethod
    async def get_default(self) -> Optional[Cashbox]:
        ...


class CashboxTransactionRepository(BaseRepository[CashboxTransaction]):
    @abstractmethod
    async def get_by_cashbox(
        self, cashbox_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CashboxTransaction], int]:
        ...

    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[CashboxTransaction], int]:
        ...


class ExtractionRepository(BaseRepository[Extraction]):
    @abstractmethod
    async def get_pending(self, page: int = 1, per_page: int = 20) -> Tuple[List[Extraction], int]:
        ...

    @abstractmethod
    async def get_by_status(
        self, status: ExtractionStatus, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Extraction], int]:
        ...


class AuditLogRepository(BaseRepository[AuditLog]):
    @abstractmethod
    async def get_by_user(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[AuditLog], int]:
        ...

    @abstractmethod
    async def get_by_resource(
        self, resource_type: str, resource_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[AuditLog], int]:
        ...

    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, per_page: int = 20
    ) -> Tuple[List[AuditLog], int]:
        ...
