from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import CustomerCreate, CustomerUpdate
from app.application.use_cases.customer_use_cases import (
    CreateCustomerUseCase,
    DeleteCustomerUseCase,
    GetCustomerStatementUseCase,
    GetCustomerUseCase,
    ListCustomersUseCase,
    UpdateCustomerUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.customer_debt_repository import CustomerDebtRepositoryImpl
from app.infrastructure.repositories.customer_repository import CustomerRepositoryImpl
from app.infrastructure.repositories.debt_payment_repository import DebtPaymentRepositoryImpl

router = APIRouter()


def _require_write(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager", "staff"):
        raise ForbiddenException("Missing permission: customers:write")
    return user


def _customer_to_dict(customer):
    return {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "address": str(customer.address) if customer.address else None,
        "tax_number": customer.tax_number,
        "credit_limit": float(customer.credit_limit.amount),
        "current_balance": float(customer.current_balance.amount),
        "is_active": customer.is_active,
        "notes": customer.notes,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
    }


@router.get("/")
async def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = CustomerRepositoryImpl(db)
    use_case = ListCustomersUseCase(repo)
    customers, total = await use_case.execute(page, per_page, search)
    return {
        "success": True,
        "data": [_customer_to_dict(c) for c in customers],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{customer_id}")
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = CustomerRepositoryImpl(db)
    use_case = GetCustomerUseCase(repo)
    customer = await use_case.execute(customer_id)
    return {"success": True, "data": _customer_to_dict(customer)}


@router.get("/{customer_id}/statement")
async def get_customer_statement(
    customer_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    customers_repo = CustomerRepositoryImpl(db)
    debts_repo = CustomerDebtRepositoryImpl(db)
    payments_repo = DebtPaymentRepositoryImpl(db)
    use_case = GetCustomerStatementUseCase(customers_repo, debts_repo, payments_repo)
    result = await use_case.execute(customer_id, page, per_page)

    customer_data = _customer_to_dict(result["customer"])
    debts_data = []
    for item in result["debt"]:
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
        "data": {"customer": customer_data, "debts": debts_data},
        "meta": result["meta"],
    }


@router.post("/")
async def create_customer(
    request: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = CustomerRepositoryImpl(db)
    use_case = CreateCustomerUseCase(repo)
    customer = await use_case.execute(
        name=request.name,
        phone=request.phone,
        email=request.email,
        address=request.address,
        tax_number=request.tax_number,
        credit_limit=request.credit_limit,
        notes=request.notes,
    )
    return {"success": True, "data": _customer_to_dict(customer), "message": "Customer created"}


@router.put("/{customer_id}")
async def update_customer(
    customer_id: str,
    request: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = CustomerRepositoryImpl(db)
    use_case = UpdateCustomerUseCase(repo)
    updates = request.model_dump(exclude_unset=True)
    customer = await use_case.execute(customer_id, updates)
    return {"success": True, "data": _customer_to_dict(customer), "message": "Customer updated"}


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_write(user)
    repo = CustomerRepositoryImpl(db)
    use_case = DeleteCustomerUseCase(repo)
    await use_case.execute(customer_id)
    return {"success": True, "message": "Customer deleted"}
