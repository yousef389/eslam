from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import SupplierCreate, SupplierUpdate
from app.application.use_cases.supplier_use_cases import (
    CreateSupplierUseCase,
    DeleteSupplierUseCase,
    GetSupplierStatementUseCase,
    GetSupplierUseCase,
    ListSuppliersUseCase,
    UpdateSupplierUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.debt_payment_repository import DebtPaymentRepositoryImpl
from app.infrastructure.repositories.supplier_debt_repository import SupplierDebtRepositoryImpl
from app.infrastructure.repositories.supplier_repository import SupplierRepositoryImpl

router = APIRouter()


def _require_write(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "staff"):
        raise ForbiddenException("Missing permission: suppliers:write")
    return user


def _supplier_to_dict(supplier):
    return {
        "id": supplier.id,
        "name": supplier.name,
        "phone": supplier.phone,
        "email": supplier.email,
        "address": str(supplier.address) if supplier.address else None,
        "tax_number": supplier.tax_number,
        "payment_terms_days": supplier.payment_terms_days,
        "is_active": supplier.is_active,
        "notes": supplier.notes,
        "created_at": supplier.created_at.isoformat() if supplier.created_at else None,
        "updated_at": supplier.updated_at.isoformat() if supplier.updated_at else None,
    }


@router.get("/")
async def list_suppliers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SupplierRepositoryImpl(db)
    use_case = ListSuppliersUseCase(repo)
    suppliers, total = await use_case.execute(page, per_page, search)
    return {
        "success": True,
        "data": [_supplier_to_dict(s) for s in suppliers],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SupplierRepositoryImpl(db)
    use_case = GetSupplierUseCase(repo)
    supplier = await use_case.execute(supplier_id)
    return {"success": True, "data": _supplier_to_dict(supplier)}


@router.get("/{supplier_id}/statement")
async def get_supplier_statement(
    supplier_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    suppliers_repo = SupplierRepositoryImpl(db)
    debts_repo = SupplierDebtRepositoryImpl(db)
    payments_repo = DebtPaymentRepositoryImpl(db)
    use_case = GetSupplierStatementUseCase(suppliers_repo, debts_repo, payments_repo)
    result = await use_case.execute(supplier_id, page, per_page)

    supplier_data = _supplier_to_dict(result["supplier"])
    debts_data = []
    for item in result["debts"]:
        debt = item["debt"]
        payments = item["payments"]
        debts_data.append({
            "debt": {
                "id": debt.id,
                "amount": float(debt.amount.amount),
                "paid_amount": float(debt.paid_amount.amount),
                "remaining": float(debt.remaining.amount),
                "status": debt.status.value,
                "description": debt.description,
                "due_date": debt.due_date.isoformat() if debt.due_date else None,
                "created_at": debt.created_at.isoformat() if debt.created_at else None,
            },
            "payments": [
                {
                    "id": p.id,
                    "amount": float(p.amount.amount),
                    "payment_method": p.payment_method.value,
                    "notes": p.notes,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in payments
            ],
        })

    return {
        "success": True,
        "data": {"supplier": supplier_data, "debts": debts_data},
        "meta": result["meta"],
    }


@router.post("/")
async def create_supplier(
    request: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = SupplierRepositoryImpl(db)
    use_case = CreateSupplierUseCase(repo)
    supplier = await use_case.execute(
        name=request.name,
        phone=request.phone,
        email=request.email,
        address=request.address,
        tax_number=request.tax_number,
        payment_terms_days=request.payment_terms_days,
        notes=request.notes,
    )
    return {"success": True, "data": _supplier_to_dict(supplier), "message": "Supplier created"}


@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: str,
    request: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = SupplierRepositoryImpl(db)
    use_case = UpdateSupplierUseCase(repo)
    updates = request.model_dump(exclude_unset=True)
    supplier = await use_case.execute(supplier_id, updates)
    return {"success": True, "data": _supplier_to_dict(supplier), "message": "Supplier updated"}


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = SupplierRepositoryImpl(db)
    use_case = DeleteSupplierUseCase(repo)
    await use_case.execute(supplier_id)
    return {"success": True, "message": "Supplier deleted"}
