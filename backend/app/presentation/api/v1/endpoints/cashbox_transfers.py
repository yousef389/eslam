from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.cashbox_repository import CashboxRepositoryImpl
from app.infrastructure.repositories.cashbox_transfer_repository import CashboxTransferRepositoryImpl
from app.domain.entities import CashboxTransfer
from app.domain.value_objects import Money

import uuid

router = APIRouter()


class CashboxTransferCreate(BaseModel):
    from_cashbox_id: str
    to_cashbox_id: str
    amount: float
    description: str = ""


def _require_accounting(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "cashier"):
        raise ForbiddenException("Missing permission: accounting:write")
    return user


def _transfer_to_dict(t):
    return {
        "id": t.id, "transfer_number": t.transfer_number,
        "from_cashbox_id": t.from_cashbox_id, "to_cashbox_id": t.to_cashbox_id,
        "amount": float(t.amount.amount), "description": t.description,
        "user_id": t.user_id,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


@router.get("/")
async def list_cashbox_transfers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = CashboxTransferRepositoryImpl(db)
    transfers, total = await repo.get_all(page, per_page)
    return {
        "success": True,
        "data": [_transfer_to_dict(t) for t in transfers],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/")
async def create_cashbox_transfer(
    request: CashboxTransferCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_accounting(user)

    if request.from_cashbox_id == request.to_cashbox_id:
        raise ValidationException("Source and destination cashboxes must be different")

    if request.amount <= 0:
        raise ValidationException("Amount must be greater than zero")

    cashbox_repo = CashboxRepositoryImpl(db)
    from_cb = await cashbox_repo.get_by_id(request.from_cashbox_id)
    to_cb = await cashbox_repo.get_by_id(request.to_cashbox_id)

    if not from_cb or not to_cb:
        raise NotFoundException("Cashbox", "not found")

    if float(from_cb.balance.amount) < request.amount:
        raise ValidationException("Insufficient balance in source cashbox")

    transfer_number = f"CT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    transfer = CashboxTransfer(
        transfer_number=transfer_number,
        from_cashbox_id=request.from_cashbox_id,
        to_cashbox_id=request.to_cashbox_id,
        amount=Money(amount=request.amount),
        description=request.description,
        user_id=user["id"],
    )

    repo = CashboxTransferRepositoryImpl(db)
    created = await repo.create(transfer)

    from_cb.balance = Money(amount=float(from_cb.balance.amount) - request.amount)
    from_cb.updated_at = datetime.utcnow()
    await cashbox_repo.update(from_cb)

    to_cb.balance = Money(amount=float(to_cb.balance.amount) + request.amount)
    to_cb.updated_at = datetime.utcnow()
    await cashbox_repo.update(to_cb)

    return {"success": True, "data": _transfer_to_dict(created), "message": "Cashbox transfer completed"}
