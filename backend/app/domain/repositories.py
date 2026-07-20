from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Generic, List, Optional, Tuple, TypeVar

from .entities import (
    AuditLog,
    Cashbox,
    CashboxTransaction,
    CashboxTransfer,
    Category,
    Customer,
    CustomerDebt,
    DebtPayment,
    Extraction,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseReturn,
    PurchaseReturnItem,
    SaleOrder,
    SaleOrderItem,
    SaleReturn,
    SaleReturnItem,
    StockMovement,
    StockTransfer,
    Supplier,
    SupplierDebt,
    SystemSetting,
    Transaction,
    User,
    Warehouse,
    WarehouseStock,
)
from .enums import DebtStatus, ExtractionStatus, SettingsGroup, StockMovementType, TransactionType

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
    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[SaleOrder], int]:
        ...

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

    @abstractmethod
    async def get_recent(self, limit: int = 10) -> Tuple[List[SaleOrder], int]:
        ...


class SaleOrderItemRepository(BaseRepository[SaleOrderItem]):
    @abstractmethod
    async def get_by_order(
        self, order_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleOrderItem], int]:
        ...


class SaleReturnRepository(BaseRepository[SaleReturn]):
    @abstractmethod
    async def get_by_return_number(self, return_number: str) -> Optional[SaleReturn]:
        ...

    @abstractmethod
    async def get_by_customer(
        self, customer_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleReturn], int]:
        ...


class SaleReturnItemRepository(BaseRepository[SaleReturnItem]):
    @abstractmethod
    async def get_by_return(
        self, return_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[SaleReturnItem], int]:
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

    @abstractmethod
    async def search(self, query: str, page: int = 1, per_page: int = 20) -> Tuple[List[PurchaseOrder], int]:
        ...


class PurchaseOrderItemRepository(BaseRepository[PurchaseOrderItem]):
    @abstractmethod
    async def get_by_order(
        self, order_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseOrderItem], int]:
        ...


class PurchaseReturnRepository(BaseRepository[PurchaseReturn]):
    @abstractmethod
    async def get_by_return_number(self, return_number: str) -> Optional[PurchaseReturn]:
        ...

    @abstractmethod
    async def get_by_supplier(
        self, supplier_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseReturn], int]:
        ...

    @abstractmethod
    async def get_by_order(
        self, order_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseReturn], int]:
        ...


class PurchaseReturnItemRepository(BaseRepository[PurchaseReturnItem]):
    @abstractmethod
    async def get_by_return(
        self, return_id: str, page: int = 1, per_page: int = 20
    ) -> Tuple[List[PurchaseReturnItem], int]:
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

    @abstractmethod
    async def get_remaining_total(self) -> float:
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

    @abstractmethod
    async def get_remaining_total(self) -> float:
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


class SystemSettingRepository(BaseRepository[SystemSetting]):
    @abstractmethod
    async def get_by_key(self, key: str) -> Optional[SystemSetting]:
        ...

    @abstractmethod
    async def get_by_group(self, group: SettingsGroup) -> List[SystemSetting]:
        ...

    @abstractmethod
    async def get_all_settings(self) -> List[SystemSetting]:
        ...

    @abstractmethod
    async def set_setting(self, key: str, value: str, group: SettingsGroup, description: str = "", is_secret: bool = False) -> SystemSetting:
        ...


class WarehouseRepository(BaseRepository[Warehouse]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Warehouse]:
        ...


class WarehouseStockRepository(BaseRepository[WarehouseStock]):
    @abstractmethod
    async def get_by_warehouse(self, warehouse_id: str) -> List[WarehouseStock]:
        ...

    @abstractmethod
    async def get_by_product(self, product_id: str) -> List[WarehouseStock]:
        ...

    @abstractmethod
    async def get_by_warehouse_and_product(self, warehouse_id: str, product_id: str) -> Optional[WarehouseStock]:
        ...


class StockMovementRepository(BaseRepository[StockMovement]):
    @abstractmethod
    async def get_by_product(self, product_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockMovement], int]:
        ...

    @abstractmethod
    async def get_by_warehouse(self, warehouse_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockMovement], int]:
        ...

    @abstractmethod
    async def get_by_type(self, movement_type: StockMovementType, page: int = 1, per_page: int = 20) -> Tuple[List[StockMovement], int]:
        ...


class StockTransferRepository(BaseRepository[StockTransfer]):
    @abstractmethod
    async def get_by_product(self, product_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockTransfer], int]:
        ...

    @abstractmethod
    async def get_by_from_warehouse(self, warehouse_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockTransfer], int]:
        ...

    @abstractmethod
    async def get_by_to_warehouse(self, warehouse_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[StockTransfer], int]:
        ...


class CashboxTransferRepository(BaseRepository[CashboxTransfer]):
    @abstractmethod
    async def get_by_from_cashbox(self, cashbox_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[CashboxTransfer], int]:
        ...

    @abstractmethod
    async def get_by_to_cashbox(self, cashbox_id: str, page: int = 1, per_page: int = 20) -> Tuple[List[CashboxTransfer], int]:
        ...
