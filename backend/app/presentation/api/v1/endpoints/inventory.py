from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.warehouse_repository import WarehouseRepositoryImpl
from app.infrastructure.repositories.warehouse_stock_repository import WarehouseStockRepositoryImpl
from app.infrastructure.repositories.stock_movement_repository import StockMovementRepositoryImpl
from app.infrastructure.repositories.stock_transfer_repository import StockTransferRepositoryImpl
from app.infrastructure.repositories.product_repository import ProductRepositoryImpl
from app.domain.entities import Warehouse, WarehouseStock, StockMovement, StockTransfer
from app.domain.enums import StockMovementType
from app.domain.value_objects import Money

import uuid

router = APIRouter()


class WarehouseCreate(BaseModel):
    name: str
    location: str = ""


class StockMovementCreate(BaseModel):
    product_id: str
    warehouse_id: str
    movement_type: str
    quantity: int
    reference_id: Optional[str] = None
    notes: str = ""


class StockTransferCreate(BaseModel):
    product_id: str
    from_warehouse_id: str
    to_warehouse_id: str
    quantity: int
    notes: str = ""


def _require_inventory(user: dict):
    role = user.get("role", "")
    if role not in ("admin", "manager"):
        raise ForbiddenException("Missing permission: inventory:write")
    return user


def _warehouse_to_dict(w):
    return {
        "id": w.id, "name": w.name, "location": w.location,
        "is_active": w.is_active,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }


def _stock_to_dict(s):
    return {
        "id": s.id, "warehouse_id": s.warehouse_id, "product_id": s.product_id,
        "quantity": s.quantity,
    }


def _movement_to_dict(m):
    return {
        "id": m.id, "movement_number": m.movement_number, "product_id": m.product_id,
        "warehouse_id": m.warehouse_id,
        "movement_type": m.movement_type.value if hasattr(m.movement_type, 'value') else m.movement_type,
        "quantity": m.quantity, "reference_id": m.reference_id, "notes": m.notes,
        "user_id": m.user_id,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


def _transfer_to_dict(t):
    return {
        "id": t.id, "transfer_number": t.transfer_number, "product_id": t.product_id,
        "from_warehouse_id": t.from_warehouse_id, "to_warehouse_id": t.to_warehouse_id,
        "quantity": t.quantity, "status": t.status, "notes": t.notes,
        "user_id": t.user_id,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


# ── Warehouses ──────────────────────────────────────────────────────────────

@router.get("/warehouses")
async def list_warehouses(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = WarehouseRepositoryImpl(db)
    warehouses, total = await repo.get_all(page, per_page)
    return {
        "success": True,
        "data": [_warehouse_to_dict(w) for w in warehouses],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/warehouses")
async def create_warehouse(
    request: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_inventory(user)
    repo = WarehouseRepositoryImpl(db)
    existing = await repo.get_by_name(request.name)
    if existing:
        raise ValidationException("Warehouse name already exists")
    warehouse = Warehouse(name=request.name, location=request.location)
    created = await repo.create(warehouse)
    return {"success": True, "data": _warehouse_to_dict(created), "message": "Warehouse created"}


@router.put("/warehouses/{warehouse_id}")
async def update_warehouse(
    warehouse_id: str,
    request: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_inventory(user)
    repo = WarehouseRepositoryImpl(db)
    warehouse = await repo.get_by_id(warehouse_id)
    if not warehouse:
        raise NotFoundException("Warehouse", warehouse_id)
    warehouse.name = request.name
    warehouse.location = request.location
    warehouse.updated_at = datetime.utcnow()
    updated = await repo.update(warehouse)
    return {"success": True, "data": _warehouse_to_dict(updated)}


@router.delete("/warehouses/{warehouse_id}")
async def delete_warehouse(
    warehouse_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_inventory(user)
    repo = WarehouseRepositoryImpl(db)
    deleted = await repo.delete(warehouse_id)
    if not deleted:
        raise NotFoundException("Warehouse", warehouse_id)
    return {"success": True, "message": "Warehouse deleted"}


# ── Stock Movements ─────────────────────────────────────────────────────────

@router.get("/stock-movements")
async def list_stock_movements(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = StockMovementRepositoryImpl(db)
    movements, total = await repo.get_all(page, per_page)
    return {
        "success": True,
        "data": [_movement_to_dict(m) for m in movements],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/stock-movements")
async def create_stock_movement(
    request: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_inventory(user)

    product_repo = ProductRepositoryImpl(db)
    product = await product_repo.get_by_id(request.product_id)
    if not product:
        raise NotFoundException("Product", request.product_id)

    warehouse_repo = WarehouseRepositoryImpl(db)
    warehouse = await warehouse_repo.get_by_id(request.warehouse_id)
    if not warehouse:
        raise NotFoundException("Warehouse", request.warehouse_id)

    movement_number = f"SM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    movement = StockMovement(
        movement_number=movement_number,
        product_id=request.product_id,
        warehouse_id=request.warehouse_id,
        movement_type=StockMovementType(request.movement_type),
        quantity=request.quantity,
        reference_id=request.reference_id,
        notes=request.notes,
        user_id=user["id"],
    )

    repo = StockMovementRepositoryImpl(db)
    created = await repo.create(movement)

    ws_repo = WarehouseStockRepositoryImpl(db)
    ws = await ws_repo.get_by_warehouse_and_product(request.warehouse_id, request.product_id)
    if ws:
        if request.movement_type in ("purchase", "return", "adjustment"):
            ws.quantity += request.quantity
        else:
            ws.quantity -= request.quantity
        ws.updated_at = datetime.utcnow()
        await ws_repo.update(ws)
    else:
        ws = WarehouseStock(
            warehouse_id=request.warehouse_id,
            product_id=request.product_id,
            quantity=request.quantity,
        )
        await ws_repo.create(ws)

    return {"success": True, "data": _movement_to_dict(created), "message": "Stock movement recorded"}


# ── Stock Transfers ─────────────────────────────────────────────────────────

@router.get("/stock-transfers")
async def list_stock_transfers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = StockTransferRepositoryImpl(db)
    transfers, total = await repo.get_all(page, per_page)
    return {
        "success": True,
        "data": [_transfer_to_dict(t) for t in transfers],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.post("/stock-transfers")
async def create_stock_transfer(
    request: StockTransferCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    _require_inventory(user)

    if request.from_warehouse_id == request.to_warehouse_id:
        raise ValidationException("Source and destination warehouses must be different")

    product_repo = ProductRepositoryImpl(db)
    product = await product_repo.get_by_id(request.product_id)
    if not product:
        raise NotFoundException("Product", request.product_id)

    warehouse_repo = WarehouseRepositoryImpl(db)
    from_wh = await warehouse_repo.get_by_id(request.from_warehouse_id)
    to_wh = await warehouse_repo.get_by_id(request.to_warehouse_id)
    if not from_wh or not to_wh:
        raise NotFoundException("Warehouse", "not found")

    ws_repo = WarehouseStockRepositoryImpl(db)
    from_stock = await ws_repo.get_by_warehouse_and_product(request.from_warehouse_id, request.product_id)
    if not from_stock or from_stock.quantity < request.quantity:
        raise ValidationException("Insufficient stock in source warehouse")

    transfer_number = f"ST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    transfer = StockTransfer(
        transfer_number=transfer_number,
        product_id=request.product_id,
        from_warehouse_id=request.from_warehouse_id,
        to_warehouse_id=request.to_warehouse_id,
        quantity=request.quantity,
        status="completed",
        notes=request.notes,
        user_id=user["id"],
    )

    repo = StockTransferRepositoryImpl(db)
    created = await repo.create(transfer)

    from_stock.quantity -= request.quantity
    from_stock.updated_at = datetime.utcnow()
    await ws_repo.update(from_stock)

    to_stock = await ws_repo.get_by_warehouse_and_product(request.to_warehouse_id, request.product_id)
    if to_stock:
        to_stock.quantity += request.quantity
        to_stock.updated_at = datetime.utcnow()
        await ws_repo.update(to_stock)
    else:
        to_stock = WarehouseStock(
            warehouse_id=request.to_warehouse_id,
            product_id=request.product_id,
            quantity=request.quantity,
        )
        await ws_repo.create(to_stock)

    return {"success": True, "data": _transfer_to_dict(created), "message": "Stock transfer completed"}


@router.get("/warehouses/{warehouse_id}/stock")
async def get_warehouse_stock(
    warehouse_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    ws_repo = WarehouseStockRepositoryImpl(db)
    stocks = await ws_repo.get_by_warehouse(warehouse_id)
    product_repo = ProductRepositoryImpl(db)
    result = []
    for s in stocks:
        product = await product_repo.get_by_id(s.product_id)
        result.append({
            **_stock_to_dict(s),
            "product_name": product.name if product else "Unknown",
            "product_sku": product.sku if product else "",
        })
    return {"success": True, "data": result}
