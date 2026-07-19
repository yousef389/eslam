from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.domain.entities import (
    CashboxTransaction,
    CustomerDebt,
    DebtPayment,
    SupplierDebt,
    Transaction,
)
from app.domain.enums import DebtStatus, DebtType, PaymentMethod, TransactionType
from app.domain.value_objects import Money


# ── Customer Debt Use Cases ────────────────────────────────────────────────────

class ListCustomerDebtsUseCase:
    def __init__(self, customer_debts_repo):
        self.customer_debts_repo = customer_debts_repo

    async def execute(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[list, int]:
        if status == "overdue":
            return await self.customer_debts_repo.get_overdue(page, per_page)
        if status == "pending":
            return await self.customer_debts_repo.get_pending(page, per_page)
        return await self.customer_debts_repo.get_all(page, per_page)


class CreateCustomerDebtUseCase:
    def __init__(self, customer_debts_repo, customers_repo):
        self.customer_debts_repo = customer_debts_repo
        self.customers_repo = customers_repo

    async def execute(
        self,
        customer_id: str,
        amount: Decimal,
        description: str,
        due_date: Optional[datetime] = None,
    ) -> CustomerDebt:
        customer = await self.customers_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)

        if amount <= 0:
            raise ValidationException("Amount must be positive")

        debt = CustomerDebt(
            customer_id=customer_id,
            amount=Money(amount=amount),
            paid_amount=Money(amount=Decimal("0")),
            remaining=Money(amount=amount),
            status=DebtStatus.PENDING,
            description=description,
            due_date=due_date,
        )

        return await self.customer_debts_repo.create(debt)


class RecordCustomerPaymentUseCase:
    def __init__(
        self,
        customer_debts_repo,
        debt_payments_repo,
        customers_repo,
    ):
        self.customer_debts_repo = customer_debts_repo
        self.debt_payments_repo = debt_payments_repo
        self.customers_repo = customers_repo

    async def execute(
        self,
        debt_id: str,
        amount: Decimal,
        user_id: str,
        payment_method: str = "cash",
        notes: Optional[str] = None,
    ) -> DebtPayment:
        debt = await self.customer_debts_repo.get_by_id(debt_id)
        if not debt:
            raise NotFoundException("Debt", debt_id)

        if debt.status == DebtStatus.PAID:
            raise ConflictException("Debt is already fully paid")

        if amount <= 0:
            raise ValidationException("Payment amount must be positive")

        if amount > debt.remaining.amount:
            raise ValidationException(
                f"Payment amount exceeds remaining balance of {debt.remaining.amount}"
            )

        try:
            pay_method = PaymentMethod(payment_method)
        except ValueError:
            raise ValidationException(f"Invalid payment method: {payment_method}")

        payment = DebtPayment(
            debt_id=debt_id,
            debt_type=DebtType.CUSTOMER,
            amount=Money(amount=amount),
            payment_method=pay_method,
            notes=notes or "",
            user_id=user_id,
        )

        created_payment = await self.debt_payments_repo.create(payment)

        debt.paid_amount = Money(amount=debt.paid_amount.amount + amount)
        debt.remaining = Money(amount=debt.amount.amount - debt.paid_amount.amount)

        if debt.remaining.amount <= 0:
            debt.status = DebtStatus.PAID
        else:
            debt.status = DebtStatus.PARTIAL

        debt.updated_at = datetime.utcnow()
        await self.customer_debts_repo.update(debt)

        customer = await self.customers_repo.get_by_id(debt.customer_id)
        if customer:
            customer.current_balance = Money(
                amount=customer.current_balance.amount - amount
            )
            customer.updated_at = datetime.utcnow()
            await self.customers_repo.update(customer)

        return created_payment


# ── Supplier Debt Use Cases ────────────────────────────────────────────────────

class ListSupplierDebtsUseCase:
    def __init__(self, supplier_debts_repo):
        self.supplier_debts_repo = supplier_debts_repo

    async def execute(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[list, int]:
        if status == "overdue":
            return await self.supplier_debts_repo.get_overdue(page, per_page)
        if status == "pending":
            return await self.supplier_debts_repo.get_pending(page, per_page)
        return await self.supplier_debts_repo.get_all(page, per_page)


class CreateSupplierDebtUseCase:
    def __init__(self, supplier_debts_repo, suppliers_repo):
        self.supplier_debts_repo = supplier_debts_repo
        self.suppliers_repo = suppliers_repo

    async def execute(
        self,
        supplier_id: str,
        amount: Decimal,
        description: str,
        due_date: Optional[datetime] = None,
    ) -> SupplierDebt:
        supplier = await self.suppliers_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", supplier_id)

        if amount <= 0:
            raise ValidationException("Amount must be positive")

        debt = SupplierDebt(
            supplier_id=supplier_id,
            amount=Money(amount=amount),
            paid_amount=Money(amount=Decimal("0")),
            remaining=Money(amount=amount),
            status=DebtStatus.PENDING,
            description=description,
            due_date=due_date,
        )

        return await self.supplier_debts_repo.create(debt)


class RecordSupplierPaymentUseCase:
    def __init__(
        self,
        supplier_debts_repo,
        debt_payments_repo,
    ):
        self.supplier_debts_repo = supplier_debts_repo
        self.debt_payments_repo = debt_payments_repo

    async def execute(
        self,
        debt_id: str,
        amount: Decimal,
        user_id: str,
        payment_method: str = "cash",
        notes: Optional[str] = None,
    ) -> DebtPayment:
        debt = await self.supplier_debts_repo.get_by_id(debt_id)
        if not debt:
            raise NotFoundException("Debt", debt_id)

        if debt.status == DebtStatus.PAID:
            raise ConflictException("Debt is already fully paid")

        if amount <= 0:
            raise ValidationException("Payment amount must be positive")

        if amount > debt.remaining.amount:
            raise ValidationException(
                f"Payment amount exceeds remaining balance of {debt.remaining.amount}"
            )

        try:
            pay_method = PaymentMethod(payment_method)
        except ValueError:
            raise ValidationException(f"Invalid payment method: {payment_method}")

        payment = DebtPayment(
            debt_id=debt_id,
            debt_type=DebtType.SUPPLIER,
            amount=Money(amount=amount),
            payment_method=pay_method,
            notes=notes or "",
            user_id=user_id,
        )

        created_payment = await self.debt_payments_repo.create(payment)

        debt.paid_amount = Money(amount=debt.paid_amount.amount + amount)
        debt.remaining = Money(amount=debt.amount.amount - debt.paid_amount.amount)

        if debt.remaining.amount <= 0:
            debt.status = DebtStatus.PAID
        else:
            debt.status = DebtStatus.PARTIAL

        debt.updated_at = datetime.utcnow()
        await self.supplier_debts_repo.update(debt)

        return created_payment


# ── Cashbox Use Cases ──────────────────────────────────────────────────────────

class ListCashboxesUseCase:
    def __init__(self, cashboxes_repo):
        self.cashboxes_repo = cashboxes_repo

    async def execute(self, page: int = 1, per_page: int = 20) -> Tuple[list, int]:
        return await self.cashboxes_repo.get_all(page, per_page)


class GetCashboxUseCase:
    def __init__(self, cashboxes_repo):
        self.cashboxes_repo = cashboxes_repo

    async def execute(self, cashbox_id: str):
        cashbox = await self.cashboxes_repo.get_by_id(cashbox_id)
        if not cashbox:
            raise NotFoundException("Cashbox", cashbox_id)
        return cashbox


class RecordCashboxTransactionUseCase:
    def __init__(
        self,
        cashboxes_repo,
        cashbox_transactions_repo,
    ):
        self.cashboxes_repo = cashboxes_repo
        self.cashbox_transactions_repo = cashbox_transactions_repo

    async def execute(
        self,
        cashbox_id: str,
        amount: Decimal,
        transaction_type: str,
        description: str,
        user_id: str,
        reference_id: Optional[str] = None,
    ) -> CashboxTransaction:
        cashbox = await self.cashboxes_repo.get_by_id(cashbox_id)
        if not cashbox:
            raise NotFoundException("Cashbox", cashbox_id)

        if not cashbox.is_active:
            raise ValidationException("Cashbox is inactive")

        try:
            tx_type = TransactionType(transaction_type)
        except ValueError:
            raise ValidationException(f"Invalid transaction type: {transaction_type}")

        if amount <= 0:
            raise ValidationException("Amount must be positive")

        if tx_type == TransactionType.EXPENSE and amount > cashbox.balance.amount:
            raise ValidationException(
                f"Insufficient balance. Current: {cashbox.balance.amount}"
            )

        cashbox_tx = CashboxTransaction(
            cashbox_id=cashbox_id,
            transaction_type=tx_type,
            amount=Money(amount=amount),
            description=description,
            reference_id=reference_id,
            user_id=user_id,
        )

        created_tx = await self.cashbox_transactions_repo.create(cashbox_tx)

        if tx_type == TransactionType.INCOME:
            cashbox.balance = Money(amount=cashbox.balance.amount + amount)
        elif tx_type == TransactionType.EXPENSE:
            cashbox.balance = Money(amount=cashbox.balance.amount - amount)

        cashbox.updated_at = datetime.utcnow()
        await self.cashboxes_repo.update(cashbox)

        return created_tx


# ── Transaction Use Cases ──────────────────────────────────────────────────────

class GetTransactionsUseCase:
    def __init__(self, transactions_repo):
        self.transactions_repo = transactions_repo

    async def execute(
        self,
        page: int = 1,
        per_page: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
    ) -> Tuple[list, int]:
        if start_date and end_date:
            return await self.transactions_repo.get_by_date_range(
                start_date, end_date, page, per_page
            )
        if transaction_type:
            try:
                tx_type = TransactionType(transaction_type)
                return await self.transactions_repo.get_by_type(tx_type, page, per_page)
            except ValueError:
                raise ValidationException(f"Invalid transaction type: {transaction_type}")
        return await self.transactions_repo.get_all(page, per_page)


# ── Reports Use Case ───────────────────────────────────────────────────────────

class GetReportsSummaryUseCase:
    def __init__(
        self,
        transactions_repo,
        sale_orders_repo,
        purchase_orders_repo,
        customer_debts_repo,
        supplier_debts_repo,
    ):
        self.transactions_repo = transactions_repo
        self.sale_orders_repo = sale_orders_repo
        self.purchase_orders_repo = purchase_orders_repo
        self.customer_debts_repo = customer_debts_repo
        self.supplier_debts_repo = supplier_debts_repo

    async def execute(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        all_sales, _ = await self.sale_orders_repo.get_by_date_range(
            start_date, end_date
        )
        total_sales = sum(o.total.amount for o in all_sales)

        all_purchases, _ = await self.purchase_orders_repo.get_by_date_range(
            start_date, end_date
        )
        total_purchases = sum(o.total.amount for o in all_purchases)

        tx_summary = await self.transactions_repo.get_summary(start_date, end_date)
        transaction_count = tx_summary.get("count", 0)

        customer_debts, _ = await self.customer_debts_repo.get_pending()
        total_receivable = sum(
            d.remaining.amount for d in customer_debts
        )

        supplier_debts, _ = await self.supplier_debts_repo.get_pending()
        total_payable = sum(
            d.remaining.amount for d in supplier_debts
        )

        net_profit = total_sales - total_purchases

        return {
            "total_sales": Decimal(str(total_sales)),
            "total_purchases": Decimal(str(total_purchases)),
            "net_profit": Decimal(str(net_profit)),
            "total_receivable": Decimal(str(total_receivable)),
            "total_payable": Decimal(str(total_payable)),
            "transaction_count": transaction_count,
        }
