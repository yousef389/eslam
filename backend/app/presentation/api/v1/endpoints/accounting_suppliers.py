from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import DebtCreate, DebtPaymentCreate
from app.application.use_cases.accounting_use_cases import (
    CreateSupplierDebtUseCase,
    ListSupplierDebtsUseCase,
    RecordSupplierPaymentUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.debt_payment_repository import DebtPaymentRepositoryImpl
from app.infrastructure.repositories.supplier_debt_repository import SupplierDebtRepositoryImpl
from app.infrastructure.repositories.supplier_repository import SupplierRepositoryImpl

router = APIRouter()


def _require_accounting(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "cashier"):
        raise ForbiddenException("Missing permission: accounting:write")
    return user


def _debt_to_dict(debt):
    return {
        "id": debt.id,
        "customer_id": getattr(debt, "customer_id", None),
        "supplier_id": getattr(debt, "supplier_id", None),
        "amount": float(debt.amount.amount),
        "paid_amount": float(debt.paid_amount.amount),
        "remaining": float(debt.remaining.amount),
        "status": debt.status.value if hasattr(debt.status, "value") else debt.status,
        "description": debt.description,
        "due_date": debt.due_date.isoformat() if debt.due_date else None,
        "created_at": debt.created_at.isoformat() if debt.created_at else None,
        "updated_at": debt.updated_at.isoformat() if debt.updated_at else None,
    }


def _payment_to_dict(payment):
    return {
        "id": payment.id,
        "debt_id": payment.debt_id,
        "amount": float(payment.amount.amount),
        "payment_method": payment.payment_method.value if hasattr(payment.payment_method, "value") else payment.payment_method,
        "notes": payment.notes,
        "user_id": payment.user_id,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
    }


@router.get("/")
async def list_supplier_debts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SupplierDebtRepositoryImpl(db)
    use_case = ListSupplierDebtsUseCase(repo)
    debts, total = await use_case.execute(page, per_page, status)
    return {
        "success": True,
        "data": [_debt_to_dict(d) for d in debts],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/")
async def create_supplier_debt(
    request: DebtCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_accounting(user)
    debts_repo = SupplierDebtRepositoryImpl(db)
    suppliers_repo = SupplierRepositoryImpl(db)
    use_case = CreateSupplierDebtUseCase(debts_repo, suppliers_repo)
    debt = await use_case.execute(
        supplier_id=request.supplier_id,
        amount=request.amount,
        description=request.description,
        due_date=request.due_date,
    )
    return {"success": True, "data": _debt_to_dict(debt), "message": "Supplier debt created"}


@router.post("/payments")
async def record_supplier_payment(
    request: DebtPaymentCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_accounting(user)
    debts_repo = SupplierDebtRepositoryImpl(db)
    payments_repo = DebtPaymentRepositoryImpl(db)
    use_case = RecordSupplierPaymentUseCase(debts_repo, payments_repo)
    payment = await use_case.execute(
        debt_id=request.debt_id,
        amount=request.amount,
        user_id=user["id"],
        payment_method=request.payment_method,
        notes=request.notes,
    )
    return {"success": True, "data": _payment_to_dict(payment), "message": "Payment recorded"}


@router.get("/{debt_id}")
async def get_supplier_debt(
    debt_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SupplierDebtRepositoryImpl(db)
    debt = await repo.get_by_id(debt_id)
    if not debt:
        raise NotFoundException("Supplier debt", debt_id)
    payments_repo = DebtPaymentRepositoryImpl(db)
    payments, _ = await payments_repo.get_by_debt(debt_id)
    return {
        "success": True,
        "data": {
            "debt": _debt_to_dict(debt),
            "payments": [_payment_to_dict(p) for p in payments],
        },
    }
