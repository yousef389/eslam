from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.accounting_use_cases import (
    GetReportsSummaryUseCase,
    GetTransactionsUseCase,
)
from app.core.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.repositories.customer_debt_repository import CustomerDebtRepositoryImpl
from app.infrastructure.repositories.purchase_order_repository import PurchaseOrderRepositoryImpl
from app.infrastructure.repositories.sale_order_repository import SaleOrderRepositoryImpl
from app.infrastructure.repositories.supplier_debt_repository import SupplierDebtRepositoryImpl
from app.infrastructure.repositories.transaction_repository import TransactionRepositoryImpl

router = APIRouter()


def _report_summary_to_dict(summary):
    return {
        "total_sales": float(summary["total_sales"]),
        "total_purchases": float(summary["total_purchases"]),
        "net_profit": float(summary["net_profit"]),
        "total_receivable": float(summary["total_receivable"]),
        "total_payable": float(summary["total_payable"]),
        "transaction_count": summary["transaction_count"],
    }


def _transaction_to_dict(tx):
    return {
        "id": tx.id,
        "transaction_number": tx.transaction_number,
        "type": tx.type.value if hasattr(tx.type, "value") else tx.type,
        "amount": float(tx.amount.amount),
        "description": tx.description,
        "reference_id": tx.reference_id,
        "reference_type": tx.reference_type,
        "user_id": tx.user_id,
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
        "updated_at": tx.updated_at.isoformat() if tx.updated_at else None,
    }


@router.get("/summary")
async def get_financial_summary(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if not from_date or not to_date:
        now = datetime.utcnow()
        from_date = from_date or now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        to_date = to_date or now

    transactions_repo = TransactionRepositoryImpl(db)
    sale_orders_repo = SaleOrderRepositoryImpl(db)
    purchase_orders_repo = PurchaseOrderRepositoryImpl(db)
    customer_debts_repo = CustomerDebtRepositoryImpl(db)
    supplier_debts_repo = SupplierDebtRepositoryImpl(db)

    use_case = GetReportsSummaryUseCase(
        transactions_repo, sale_orders_repo, purchase_orders_repo,
        customer_debts_repo, supplier_debts_repo,
    )
    summary = await use_case.execute(from_date, to_date)
    return {"success": True, "data": _report_summary_to_dict(summary)}


@router.get("/transactions")
async def list_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    transaction_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = TransactionRepositoryImpl(db)
    use_case = GetTransactionsUseCase(repo)
    transactions, total = await use_case.execute(
        page, per_page, from_date, to_date, transaction_type
    )
    return {
        "success": True,
        "data": [_transaction_to_dict(tx) for tx in transactions],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }
