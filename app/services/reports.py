from datetime import datetime, time

from sqlalchemy import func

from app.models import (Category, Inventory, Order, OrderItem, Payment, Product, Refund, ReturnRequest,
                        Warehouse)
from app.utils import money


def _date_filter(q, column, date_from=None, date_to=None):
    if date_from:
        q = q.filter(column >= datetime.combine(date_from, time.min))
    if date_to:
        q = q.filter(column <= datetime.combine(date_to, time.max))
    return q


def sales_report(db, date_from=None, date_to=None, status=None, category_id=None):
    day = func.date(Order.created_at)
    q = db.query(day.label("day"), func.count(func.distinct(Order.id)), func.coalesce(func.sum(Order.grand_total), 0))
    if category_id:
        q = q.join(OrderItem, OrderItem.order_id == Order.id).join(Product, Product.id == OrderItem.product_id) \
             .filter(Product.category_id == category_id)
    q = _date_filter(q, Order.created_at, date_from, date_to)
    if status:
        q = q.filter(Order.status == status)
    else:
        q = q.filter(Order.status != "cancelled")
    rows = q.group_by(day).order_by(day).all()
    return [{"date": str(d), "orders": c, "revenue": str(money(r))} for d, c, r in rows]


def order_status_counts(db, date_from=None, date_to=None):
    q = db.query(Order.status, func.count(Order.id))
    q = _date_filter(q, Order.created_at, date_from, date_to)
    return {s: c for s, c in q.group_by(Order.status).all()}


def inventory_report(db, warehouse_id=None, category_id=None):
    q = db.query(Inventory, Product, Warehouse).join(Product, Product.id == Inventory.product_id) \
          .join(Warehouse, Warehouse.id == Inventory.warehouse_id)
    if warehouse_id:
        q = q.filter(Inventory.warehouse_id == warehouse_id)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    out = []
    for inv, product, wh in q.order_by(Product.name).all():
        out.append({
            "product_id": product.id, "product": product.name, "sku": product.sku,
            "variant_id": inv.variant_id, "warehouse": wh.code,
            "on_hand": inv.quantity, "reserved": inv.reserved, "available": inv.available,
            "threshold": inv.min_threshold, "low_stock": inv.available <= (inv.min_threshold or 0),
        })
    return out


def payments_report(db, date_from=None, date_to=None, status=None):
    q = db.query(Payment)
    q = _date_filter(q, Payment.created_at, date_from, date_to)
    if status:
        q = q.filter(Payment.status == status)
    rows = []
    for p in q.order_by(Payment.created_at).all():
        rows.append({"payment_id": p.id, "order_id": p.order_id, "amount": str(p.amount), "method": p.method,
                     "gateway": p.gateway, "status": p.status, "date": p.created_at.isoformat()})
    return rows


def refunds_report(db, date_from=None, date_to=None, status=None):
    q = db.query(Refund)
    q = _date_filter(q, Refund.created_at, date_from, date_to)
    if status:
        q = q.filter(Refund.status == status)
    return [{"refund_no": r.refund_no, "order_id": r.order_id, "amount": str(r.amount), "status": r.status,
             "reason": r.reason, "date": r.created_at.isoformat()} for r in q.order_by(Refund.created_at).all()]


def product_performance(db, date_from=None, date_to=None, category_id=None, limit=50):
    q = db.query(Product.id, Product.name, func.sum(OrderItem.quantity), func.sum(OrderItem.line_total)) \
          .join(OrderItem, OrderItem.product_id == Product.id) \
          .join(Order, Order.id == OrderItem.order_id) \
          .filter(Order.status != "cancelled")
    q = _date_filter(q, Order.created_at, date_from, date_to)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    rows = q.group_by(Product.id, Product.name).order_by(func.sum(OrderItem.line_total).desc()).limit(limit).all()
    return [{"product_id": i, "product": n, "units_sold": int(u or 0), "revenue": str(money(r))} for i, n, u, r in rows]


def category_performance(db, date_from=None, date_to=None):
    q = db.query(Category.id, Category.name, func.sum(OrderItem.quantity), func.sum(OrderItem.line_total)) \
          .join(Product, Product.category_id == Category.id) \
          .join(OrderItem, OrderItem.product_id == Product.id) \
          .join(Order, Order.id == OrderItem.order_id) \
          .filter(Order.status != "cancelled")
    q = _date_filter(q, Order.created_at, date_from, date_to)
    rows = q.group_by(Category.id, Category.name).all()
    return [{"category_id": i, "category": n, "units_sold": int(u or 0), "revenue": str(money(r))} for i, n, u, r in rows]


def returns_summary(db):
    return {s: c for s, c in db.query(ReturnRequest.status, func.count(ReturnRequest.id))
            .group_by(ReturnRequest.status).all()}


REPORTS = {
    "sales": lambda db, f: sales_report(db, f.get("date_from"), f.get("date_to"), f.get("status"), f.get("category_id")),
    "inventory": lambda db, f: inventory_report(db, f.get("warehouse_id"), f.get("category_id")),
    "payments": lambda db, f: payments_report(db, f.get("date_from"), f.get("date_to"), f.get("status")),
    "refunds": lambda db, f: refunds_report(db, f.get("date_from"), f.get("date_to"), f.get("status")),
    "products": lambda db, f: product_performance(db, f.get("date_from"), f.get("date_to"), f.get("category_id")),
}