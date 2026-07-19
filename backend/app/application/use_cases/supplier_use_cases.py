from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException
from app.domain.entities import Supplier
from app.domain.value_objects import Address, Money


class ListSuppliersUseCase:
    def __init__(self, suppliers_repo):
        self.suppliers_repo = suppliers_repo

    async def execute(
        self, page: int = 1, per_page: int = 20, search: Optional[str] = None
    ) -> Tuple[list, int]:
        if search:
            return await self.suppliers_repo.search(search, page, per_page)
        return await self.suppliers_repo.get_all(page, per_page)


class GetSupplierUseCase:
    def __init__(self, suppliers_repo):
        self.suppliers_repo = suppliers_repo

    async def execute(self, supplier_id: str) -> Supplier:
        supplier = await self.suppliers_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", supplier_id)
        return supplier


class CreateSupplierUseCase:
    def __init__(self, suppliers_repo):
        self.suppliers_repo = suppliers_repo

    async def execute(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        tax_number: Optional[str] = None,
        payment_terms_days: int = 30,
        notes: Optional[str] = None,
    ) -> Supplier:
        existing = await self.suppliers_repo.get_by_name(name)
        if existing:
            raise ConflictException(f"Supplier '{name}' already exists")

        supplier = Supplier(
            name=name,
            phone=phone,
            email=email,
            address=Address(street=address) if address else None,
            tax_number=tax_number,
            payment_terms_days=payment_terms_days,
            notes=notes or "",
        )

        return await self.suppliers_repo.create(supplier)


class UpdateSupplierUseCase:
    def __init__(self, suppliers_repo):
        self.suppliers_repo = suppliers_repo

    async def execute(self, supplier_id: str, updates: dict) -> Supplier:
        supplier = await self.suppliers_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", supplier_id)

        if "name" in updates and updates["name"] is not None:
            existing = await self.suppliers_repo.get_by_name(updates["name"])
            if existing and existing.id != supplier_id:
                raise ConflictException(f"Supplier name already in use")

        if "address" in updates:
            addr = updates["address"]
            if addr is not None:
                supplier.address = Address(street=addr)
            else:
                supplier.address = None

        for field in [
            "name", "phone", "email", "tax_number",
            "payment_terms_days", "notes", "is_active",
        ]:
            if field in updates and updates[field] is not None:
                setattr(supplier, field, updates[field])

        supplier.updated_at = datetime.utcnow()
        return await self.suppliers_repo.update(supplier)


class DeleteSupplierUseCase:
    def __init__(self, suppliers_repo):
        self.suppliers_repo = suppliers_repo

    async def execute(self, supplier_id: str) -> None:
        supplier = await self.suppliers_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", supplier_id)

        supplier.is_active = False
        supplier.updated_at = datetime.utcnow()
        await self.suppliers_repo.update(supplier)


class GetSupplierStatementUseCase:
    def __init__(self, suppliers_repo, supplier_debts_repo, debt_payments_repo):
        self.suppliers_repo = suppliers_repo
        self.supplier_debts_repo = supplier_debts_repo
        self.debt_payments_repo = debt_payments_repo

    async def execute(
        self,
        supplier_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        supplier = await self.suppliers_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException("Supplier", supplier_id)

        debts, total = await self.supplier_debts_repo.get_by_supplier(
            supplier_id, page, per_page
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
            "supplier": supplier,
            "debts": debts_with_payments,
            "meta": {
                "total": total,
                "page": page,
                "per_page": per_page,
            },
        }
