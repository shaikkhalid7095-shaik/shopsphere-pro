# Module 13 inventory, 14 warehouses, 15 transfers, 16 low stock
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import (Inventory, Product, ProductVariant, RestockAlert, StockMovement, StockTransfer,
                        ThresholdHistory, User, Warehouse)
from app.roles import ADMIN, INVENTORY_MANAGER, ORDER_MANAGER
from app.schemas.common import Page
from app.schemas.inventory import (AlertOut, MovementOut, StockAdjustIn, StockOut, ThresholdHistoryOut,
                                   ThresholdIn, TransferIn, TransferOut, TransferQtyIn, WarehouseIn,
                                   WarehouseOut)
from app.services import stock
from app.services.audit import log_action
from app.services.reports import inventory_report
from app.utils import get_or_404, make_code, paginate

router = APIRouter(tags=["13. Inventory, 14. Warehouses, 15. Transfers, 16. Low Stock"])
inv_staff = require_roles(ADMIN, INVENTORY_MANAGER)
inv_viewers = require_roles(ADMIN, INVENTORY_MANAGER, ORDER_MANAGER)


def _check_product(db, product_id, variant_id):
    get_or_404(db, Product, product_id, "Product")
    if variant_id:
        v = db.get(ProductVariant, variant_id)
        if not v or v.product_id != product_id:
            raise HTTPException(400, "Variant does not belong to product")


# ---------------- warehouses ----------------
@router.get("/warehouses", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), _=Depends(inv_viewers)):
    return db.query(Warehouse).order_by(Warehouse.code).all()


@router.post("/warehouses", response_model=WarehouseOut, status_code=201)
def create_warehouse(data: WarehouseIn, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    if db.query(Warehouse).filter_by(code=data.code.upper()).first():
        raise HTTPException(409, "Warehouse code exists")
    wh = Warehouse(**data.model_dump())
    wh.code = wh.code.upper()
    db.add(wh)
    db.commit()
    return wh


@router.put("/warehouses/{wh_id}", response_model=WarehouseOut)
def update_warehouse(wh_id: int, data: WarehouseIn, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    wh = get_or_404(db, Warehouse, wh_id, "Warehouse")
    used = sum(r.quantity for r in db.query(Inventory).filter_by(warehouse_id=wh_id).all())
    if data.capacity < used:
        raise HTTPException(400, f"Capacity can't be lower than current stock ({used})")
    for k, v in data.model_dump().items():
        setattr(wh, k, v)
    wh.code = wh.code.upper()
    db.commit()
    return wh


@router.get("/warehouses/{wh_id}/stock")
def warehouse_stock(wh_id: int, db: Session = Depends(get_db), _=Depends(inv_viewers)):
    wh = get_or_404(db, Warehouse, wh_id, "Warehouse")
    rows = inventory_report(db, warehouse_id=wh_id)
    used = sum(r["on_hand"] for r in rows)
    return {"warehouse": wh.code, "capacity": wh.capacity, "used": used,
            "utilisation_pct": round(used * 100 / wh.capacity, 2) if wh.capacity else None, "items": rows}


# ---------------- inventory ----------------
@router.get("/inventory", response_model=Page[StockOut])
def list_stock(product_id: Optional[int] = None, variant_id: Optional[int] = None,
               warehouse_id: Optional[int] = None, page: int = 1, size: int = 50,
               db: Session = Depends(get_db), _=Depends(inv_viewers)):
    q = db.query(Inventory)
    if product_id:
        q = q.filter(Inventory.product_id == product_id)
    if variant_id:
        q = q.filter(Inventory.variant_id == variant_id)
    if warehouse_id:
        q = q.filter(Inventory.warehouse_id == warehouse_id)
    return paginate(q.order_by(Inventory.id), page, size)


@router.get("/inventory/product/{product_id}")
def stock_for_product(product_id: int, variant_id: Optional[int] = None, db: Session = Depends(get_db),
                      _=Depends(inv_viewers)):
    _check_product(db, product_id, variant_id)
    q = db.query(Inventory).filter(Inventory.product_id == product_id)
    if variant_id:
        q = q.filter(Inventory.variant_id == variant_id)
    rows = q.all()
    return {
        "product_id": product_id, "variant_id": variant_id,
        "on_hand": sum(r.quantity for r in rows), "reserved": sum(r.reserved for r in rows),
        "available": sum(r.available for r in rows),
        "by_warehouse": [StockOut.model_validate(r) for r in rows],
    }


@router.post("/inventory/adjust", response_model=StockOut)
def adjust_stock(data: StockAdjustIn, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    _check_product(db, data.product_id, data.variant_id)
    wh = get_or_404(db, Warehouse, data.warehouse_id, "Warehouse")
    if not wh.is_active:
        raise HTTPException(400, "Warehouse is inactive")
    row = stock.get_or_create_row(db, data.product_id, data.variant_id, data.warehouse_id)
    before = row.quantity
    if data.action == "add":
        stock.add_stock(db, row, data.quantity, "add", "manual", data.note, me.id)
    else:
        stock.remove_stock(db, row, data.quantity, "remove", "manual", data.note, me.id)
    log_action(db, me.id, f"inventory.{data.action}", "inventory", row.id, {"quantity": before},
               {"quantity": row.quantity})
    db.commit()
    db.refresh(row)
    return row


@router.get("/inventory/{inventory_id}/movements", response_model=Page[MovementOut])
def movements(inventory_id: int, page: int = 1, size: int = 50, db: Session = Depends(get_db),
              _=Depends(inv_viewers)):
    q = db.query(StockMovement).filter_by(inventory_id=inventory_id).order_by(StockMovement.id.desc())
    return paginate(q, page, size)


# ---------------- transfers ----------------
@router.post("/inventory/transfers", response_model=TransferOut, status_code=201)
def create_transfer(data: TransferIn, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    _check_product(db, data.product_id, data.variant_id)
    src = get_or_404(db, Warehouse, data.from_warehouse_id, "Source warehouse")
    dst = get_or_404(db, Warehouse, data.to_warehouse_id, "Destination warehouse")
    if not src.is_active or not dst.is_active:
        raise HTTPException(400, "Both warehouses must be active")
    if stock.total_available(db, data.product_id, data.variant_id) <= 0:
        raise HTTPException(400, "No stock available for this product")
    t = StockTransfer(transfer_no=make_code("TR"), created_by=me.id, **data.model_dump())
    db.add(t)
    db.commit()
    return t


@router.get("/inventory/transfers", response_model=Page[TransferOut])
def list_transfers(status: Optional[str] = None, page: int = 1, size: int = 20, db: Session = Depends(get_db),
                   _=Depends(inv_staff)):
    q = db.query(StockTransfer)
    if status:
        q = q.filter_by(status=status)
    return paginate(q.order_by(StockTransfer.id.desc()), page, size)


@router.post("/inventory/transfers/{t_id}/dispatch", response_model=TransferOut)
def dispatch_transfer(t_id: int, data: TransferQtyIn, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    t = get_or_404(db, StockTransfer, t_id, "Transfer")
    if t.status != "requested":
        raise HTTPException(400, f"Transfer is {t.status}")
    if data.quantity > t.quantity:
        raise HTTPException(400, "Can't dispatch more than requested")
    src = stock.get_or_create_row(db, t.product_id, t.variant_id, t.from_warehouse_id)
    stock.remove_stock(db, src, data.quantity, "transfer_out", t.transfer_no, None, me.id)
    t.dispatched_qty = data.quantity
    t.status = "dispatched"
    log_action(db, me.id, "transfer.dispatch", "transfer", t.id, None, {"qty": data.quantity})
    db.commit()
    return t


@router.post("/inventory/transfers/{t_id}/receive", response_model=TransferOut)
def receive_transfer(t_id: int, data: TransferQtyIn, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    t = get_or_404(db, StockTransfer, t_id, "Transfer")
    if t.status != "dispatched":
        raise HTTPException(400, "Transfer must be dispatched first")
    if data.quantity > t.dispatched_qty:
        raise HTTPException(400, "Received more than dispatched")
    dst = stock.get_or_create_row(db, t.product_id, t.variant_id, t.to_warehouse_id)
    stock.add_stock(db, dst, data.quantity, "transfer_in", t.transfer_no, None, me.id)
    t.received_qty = data.quantity
    t.status = "received"
    if data.quantity < t.dispatched_qty:
        t.note = f"{(t.note or '')} short received by {t.dispatched_qty - data.quantity}".strip()
    log_action(db, me.id, "transfer.receive", "transfer", t.id, None, {"qty": data.quantity})
    db.commit()
    return t


@router.post("/inventory/transfers/{t_id}/cancel", response_model=TransferOut)
def cancel_transfer(t_id: int, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    t = get_or_404(db, StockTransfer, t_id, "Transfer")
    if t.status != "requested":
        raise HTTPException(400, "Only requested transfers can be cancelled")
    t.status = "cancelled"
    db.commit()
    return t


# ---------------- low stock ----------------
@router.put("/inventory/{inventory_id}/threshold", response_model=StockOut)
def set_threshold(inventory_id: int, data: ThresholdIn, db: Session = Depends(get_db), me: User = Depends(inv_staff)):
    row = get_or_404(db, Inventory, inventory_id, "Inventory row")
    db.add(ThresholdHistory(inventory_id=row.id, old_value=row.min_threshold, new_value=data.min_threshold,
                            changed_by=me.id))
    row.min_threshold = data.min_threshold
    stock.check_low_stock(db, row)
    db.commit()
    return row


@router.get("/inventory/{inventory_id}/threshold-history", response_model=list[ThresholdHistoryOut])
def threshold_history(inventory_id: int, db: Session = Depends(get_db), _=Depends(inv_staff)):
    return db.query(ThresholdHistory).filter_by(inventory_id=inventory_id).order_by(ThresholdHistory.id.desc()).all()


@router.get("/inventory/low-stock")
def low_stock(warehouse_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(inv_viewers)):
    rows = [r for r in inventory_report(db, warehouse_id=warehouse_id) if r["low_stock"]]
    return {"count": len(rows), "items": rows}


@router.get("/inventory/alerts", response_model=Page[AlertOut])
def restock_alerts(status: str = "open", page: int = 1, size: int = 50, db: Session = Depends(get_db),
                   _=Depends(inv_staff)):
    q = db.query(RestockAlert).filter_by(status=status).order_by(RestockAlert.id.desc())
    return paginate(q, page, size)