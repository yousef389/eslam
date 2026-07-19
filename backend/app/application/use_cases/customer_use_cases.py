from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.domain.entities import Customer
from app.domain.value_objects import Address, Money


class ListCustomersUseCase:
    def __init__(self, customers_repo):
        self.customers_repo = customers_repo

    async def execute(
        self, page: int = 1, per_page: int = 20, search: Optional[str] = None
    ) -> Tuple[list, int]:
        if search:
            return await self.customers_repo.search(search, page, per_page)
        return await self.customers_repo.get_all(page, per_page)


class GetCustomerUseCase:
    def __init__(self, customers_repo):
        self.customers_repo = customers_repo

    async def execute(self, customer_id: str) -> Customer:
        customer = await self.customers_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)
        return customer


class CreateCustomerUseCase:
    def __init__(self, customers_repo):
        self.customers_repo = customers_repo

    async def execute(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        tax_number: Optional[str] = None,
        credit_limit: Decimal = Decimal("0"),
        notes: Optional[str] = None,
    ) -> Customer:
        existing = await self.customers_repo.get_by_phone(phone)
        if existing:
            raise ConflictException(f"Customer with phone '{phone}' already exists")

        customer = Customer(
            name=name,
            phone=phone,
            email=email,
            address=Address(street=address) if address else None,
            tax_number=tax_number,
            credit_limit=Money(amount=credit_limit),
            notes=notes or "",
        )

        return await self.customers_repo.create(customer)


class UpdateCustomerUseCase:
    def __init__(self, customers_repo):
        self.customers_repo = customers_repo

    async def execute(self, customer_id: str, updates: dict) -> Customer:
        customer = await self.customers_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)

        if "phone" in updates and updates["phone"] is not None:
            existing = await self.customers_repo.get_by_phone(updates["phone"])
            if existing and existing.id != customer_id:
                raise ConflictException(f"Phone number already in use")

        if "credit_limit" in updates and updates["credit_limit"] is not None:
            customer.credit_limit = Money(amount=updates["credit_limit"])

        if "address" in updates:
            addr = updates["address"]
            if addr is not None:
                customer.address = Address(street=addr)
            else:
                customer.address = None

        for field in [
            "name", "phone", "email", "tax_number", "notes", "is_active",
        ]:
            if field in updates and updates[field] is not None:
                setattr(customer, field, updates[field])

        customer.updated_at = datetime.utcnow()
        return await self.customers_repo.update(customer)


class DeleteCustomerUseCase:
    def __init__(self, customers_repo):
        self.customers_repo = customers_repo

    async def execute(self, customer_id: str) -> None:
        customer = await self.customers_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)

        customer.is_active = False
        customer.updated_at = datetime.utcnow()
        await self.customers_repo.update(customer)


class GetCustomerStatementUseCase:
    def __init__(self, customers_repo, customer_debts_repo, debt_payments_repo):
        self.customers_repo = customers_repo
        self.customer_debts_repo = customer_debts_repo
        self.debt_payments_repo = debt_payments_repo

    async def execute(
        self,
        customer_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        customer = await self.customers_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)

        debts, total = await self.customer_debts_repo.get_by_customer(
            customer_id, page, per_page
        )

        debts_with_payments = []
        for debt in debts:
            payments, _ = await self.debt_payments_repo.get_by_debt(debt.id)
            debts_with_payments.append(
                {
                    "debt": debt,
                    "payments": payments,
                }
            )

        return {
            "customer": customer,
            "debts": debts_with_payments,
            "meta": {
                "total": total,
                "page": page,
                "per_page": per_page,
            },
        }
