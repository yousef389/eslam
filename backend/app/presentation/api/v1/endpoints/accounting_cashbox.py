from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import CashboxTransactionCreate
from app.application.use_cases.accounting_use_cases import (
    GetCashboxUseCase,
    ListCashboxesUseCase,
    RecordCashboxTransactionUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.cashbox_repository import CashboxRepositoryImpl
from app.infrastructure.repositories.cashbox_transaction_repository import CashboxTransactionRepositoryImpl

router = APIRouter()


def _require_accounting(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "cashier"):
        raise ForbiddenException("Missing permission: accounting:write")
    return user


def _cashbox_to_dict(cashbox):
    return {
        "id": cashbox.id,
        "name": cashbox.name,
        "balance": float(cashbox.balance.amount),
        "is_active": cashbox.is_active,
        "created_at": cashbox.created_at.isoformat() if cashbox.created_at else None,
        "updated_at": cashbox.updated_at.isoformat() if cashbox.updated_at else None,
    }


def _transaction_to_dict(tx):
    return {
        "id": tx.id,
        "cashbox_id": tx.cashbox_id,
        "transaction_type": tx.transaction_type.value if hasattr(tx.transaction_type, "value") else tx.transaction_type,
        "amount": float(tx.amount.amount),
        "description": tx.description,
        "reference_id": tx.reference_id,
        "user_id": tx.user_id,
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
    }


@router.get("/")
async def list_cashboxes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = CashboxRepositoryImpl(db)
    use_case = ListCashboxesUseCase(repo)
    cashboxes, total = await use_case.execute(page, per_page)
    return {
        "success": True,
        "data": [_cashbox_to_dict(c) for c in cashboxes],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{cashbox_id}")
async def get_cashbox(
    cashbox_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = CashboxRepositoryImpl(db)
    use_case = GetCashboxUseCase(repo)
    cashbox = await use_case.execute(cashbox_id)
    return {"success": True, "data": _cashbox_to_dict(cashbox)}


@router.post("/{cashbox_id}/transactions")
async def record_cashbox_transaction(
    cashbox_id: str,
    request: CashboxTransactionCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_accounting(user)
    cashboxes_repo = CashboxRepositoryImpl(db)
    tx_repo = CashboxTransactionRepositoryImpl(db)
    use_case = RecordCashboxTransactionUseCase(cashboxes_repo, tx_repo)
    tx = await use_case.execute(
        cashbox_id=cashbox_id,
        amount=request.amount,
        transaction_type=request.transaction_type,
        description=request.description,
        user_id=user["id"],
        reference_id=request.reference_id,
    )
    return {"success": True, "data": _transaction_to_dict(tx), "message": "Transaction recorded"}


@router.get("/{cashbox_id}/transactions")
async def list_cashbox_transactions(
    cashbox_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    cashboxes_repo = CashboxRepositoryImpl(db)
    use_case = GetCashboxUseCase(cashboxes_repo)
    cashbox = await use_case.execute(cashbox_id)

    tx_repo = CashboxTransactionRepositoryImpl(db)
    transactions, total = await tx_repo.get_by_cashbox(cashbox_id, page, per_page)
    return {
        "success": True,
        "data": [_transaction_to_dict(tx) for tx in transactions],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }
