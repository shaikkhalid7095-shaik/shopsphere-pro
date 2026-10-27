from fastapi import HTTPException
from sqlalchemy import func

from app.models import Inventory, RestockAlert, StockMovement, Warehouse
from app.roles import INVENTORY_MANAGER
from app.services.notify import notify_roles
from app.utils import now


def _stock_query(db, product_id, variant_id):
    q = db.query(Inventory).join(Warehouse).filter(
        Inventory.product_id == product_id, Warehouse.is_active.is_(True))
    if variant_id:
        q = q.filter(Inventory.variant_id == variant_id)
    else:
        q = q.filter(Inventory.variant_id.is_(None))
    return q


def total_available(db, product_id, variant_id=None) -> int:
    rows = _stock_query(db, product_id, variant_id).all()
    return sum(r.available for r in rows)


def find_stock_row(db, product_id, variant_id, qty, lock=True):
    """pick one warehouse that can cover the whole quantity. row is locked (SELECT ... FOR UPDATE)"""
    q = _stock_query(db, product_id, variant_id)
    if lock:
        q = q.with_for_update()
    rows = sorted(q.all(), key=lambda r: r.available, reverse=True)
    if not rows or rows[0].available < qty:
        return None
    return rows[0]


def get_or_create_row(db, product_id, variant_id, warehouse_id):
    q = db.query(Inventory).filter_by(product_id=product_id, warehouse_id=warehouse_id)
    q = q.filter(Inventory.variant_id == variant_id) if variant_id else q.filter(Inventory.variant_id.is_(None))
    row = q.with_for_update().first()
    if not row:
        row = Inventory(product_id=product_id, variant_id=variant_id, warehouse_id=warehouse_id,
                        quantity=0, reserved=0)
        db.add(row)
        db.flush()
    return row


def _move(db, row, change, kind, reference=None, note=None, user_id=None):
    db.add(StockMovement(inventory_id=row.id, change=change, movement_type=kind,
                         reference=reference, note=note, created_by=user_id))


def add_stock(db, row, qty, kind="add", reference=None, note=None, user_id=None):
    if qty <= 0:
        raise HTTPException(400, "Quantity must be positive")
    wh = row.warehouse or db.get(Warehouse, row.warehouse_id)
    if wh and wh.capacity is not None:
        used = db.query(func.coalesce(func.sum(Inventory.quantity), 0)).filter(
            Inventory.warehouse_id == row.warehouse_id).scalar()
        if used + qty > wh.capacity:
            raise HTTPException(400, f"Warehouse capacity exceeded ({used}/{wh.capacity})")
    row.quantity += qty
    _move(db, row, qty, kind, reference, note, user_id)
    check_low_stock(db, row)


def remove_stock(db, row, qty, kind="remove", reference=None, note=None, user_id=None):
    if qty <= 0:
        raise HTTPException(400, "Quantity must be positive")
    if row.available < qty:
        raise HTTPException(400, f"Not enough stock. Available: {row.available}")
    row.quantity -= qty
    _move(db, row, -qty, kind, reference, note, user_id)
    check_low_stock(db, row)


def reserve(db, row, qty, reference=None, user_id=None):
    if row.available < qty:
        raise HTTPException(409, "Stock just ran out for one of the items")
    row.reserved += qty
    _move(db, row, qty, "reserve", reference, None, user_id)
    check_low_stock(db, row)


def release(db, row, qty, reference=None, user_id=None):
    qty = min(qty, row.reserved)
    if qty <= 0:
        return
    row.reserved -= qty
    _move(db, row, qty, "release", reference, None, user_id)
    check_low_stock(db, row)


def consume_reserved(db, row, qty, reference=None, user_id=None):
    """when order ships - reserved stock actually leaves the warehouse"""
    qty_from_reserved = min(qty, row.reserved)
    row.reserved -= qty_from_reserved
    if row.quantity < qty:
        raise HTTPException(400, "Inventory would go negative")
    row.quantity -= qty
    _move(db, row, -qty, "sale", reference, None, user_id)


def check_low_stock(db, row):
    open_alert = db.query(RestockAlert).filter_by(inventory_id=row.id, status="open").first()
    if row.available <= (row.min_threshold or 0):
        if not open_alert:
            db.add(RestockAlert(inventory_id=row.id, available_qty=row.available, threshold=row.min_threshold))
            notify_roles(db, [INVENTORY_MANAGER], "Low stock alert",
                         f"Inventory row #{row.id} (product {row.product_id}) is down to {row.available}",
                         kind="inventory")
    elif open_alert:
        open_alert.status = "resolved"
        open_alert.resolved_at = now()