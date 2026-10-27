# Module 36 returns, Module 37 exchanges
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import check_owner, get_current_user, require_customer, require_roles
from app.models import (ExchangeEvent, ExchangeRequest, Inventory, Order, OrderItem, OrderStatusHistory,
                        ProductVariant, ReturnItem, ReturnRequest, User, Warehouse)
from app.roles import ADMIN, ORDER_MANAGER, SUPPORT_AGENT
from app.schemas.common import Page
from app.schemas.logistics import (ExchangeDetail, ExchangeEventOut, ExchangeIn, ExchangeOut, ReceiveIn, ReturnIn,
                                   ReturnOut, ReviewDecisionIn)
from app.services import orders as order_service
from app.services import stock
from app.services.audit import log_action
from app.services.notify import notify_user
from app.utils import get_or_404, make_code, money, now, paginate

router = APIRouter(tags=["36. Returns, 37. Exchanges"])
returns_staff = require_roles(ADMIN, ORDER_MANAGER)


def _delivered_at(db, order):
    h = (db.query(OrderStatusHistory).filter_by(order_id=order.id, to_status="delivered")
         .order_by(OrderStatusHistory.id.desc()).first())
    return h.created_at if h else None


def _check_window(db, order):
    if order.status != "delivered":
        raise HTTPException(400, "Only delivered orders can be returned or exchanged")
    delivered = _delivered_at(db, order)
    if delivered and now() - delivered > timedelta(days=settings.return_window_days):
        raise HTTPException(400, f"Return window of {settings.return_window_days} days has passed")


def _already_returned(db, order_item_id):
    total = db.query(func.coalesce(func.sum(ReturnItem.quantity), 0)).join(ReturnRequest).filter(
        ReturnItem.order_item_id == order_item_id,
        ReturnRequest.status.notin_(["rejected"])).scalar()
    exch = db.query(func.coalesce(func.sum(ExchangeRequest.quantity), 0)).filter(
        ExchangeRequest.order_item_id == order_item_id,
        ExchangeRequest.status.notin_(["rejected"])).scalar()
    return int(total) + int(exch)


# ---------------- returns ----------------
@router.post("/returns", response_model=ReturnOut, status_code=201)
def request_return(data: ReturnIn, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    order = db.get(Order, data.order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(404, "Order not found")
    _check_window(db, order)

    items_by_id = {i.id: i for i in order.items}
    ret = ReturnRequest(return_no=make_code("RET"), order_id=order.id, user_id=user.id, reason=data.reason)
    seen = set()
    for it in data.items:
        oi = items_by_id.get(it.order_item_id)
        if not oi:
            raise HTTPException(400, f"Item {it.order_item_id} is not part of this order")
        if it.order_item_id in seen:
            raise HTTPException(400, "Same item listed twice")
        seen.add(it.order_item_id)
        left = oi.quantity - _already_returned(db, oi.id)
        if it.quantity > left:
            raise HTTPException(400, f"Only {left} of {oi.product_name} can still be returned")
        ret.items.append(ReturnItem(order_item_id=oi.id, quantity=it.quantity, reason=it.reason))
    db.add(ret)
    db.commit()
    return ret


@router.get("/returns", response_model=Page[ReturnOut])
def list_returns(status: Optional[str] = None, page: int = 1, size: int = 20,
                 user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(ReturnRequest)
    if user.role_name not in (ADMIN, ORDER_MANAGER, SUPPORT_AGENT, "super_admin"):
        q = q.filter(ReturnRequest.user_id == user.id)
    if status:
        q = q.filter(ReturnRequest.status == status)
    return paginate(q.order_by(ReturnRequest.id.desc()), page, size)


@router.get("/returns/{return_id}", response_model=ReturnOut)
def get_return(return_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = get_or_404(db, ReturnRequest, return_id, "Return")
    check_owner(user, r.user_id, ADMIN, ORDER_MANAGER, SUPPORT_AGENT)
    return r


@router.post("/returns/{return_id}/review", response_model=ReturnOut)
def review_return(return_id: int, data: ReviewDecisionIn, db: Session = Depends(get_db),
                  me: User = Depends(returns_staff)):
    r = get_or_404(db, ReturnRequest, return_id, "Return")
    if r.status != "requested":
        raise HTTPException(400, f"Return is already {r.status}")
    r.status = "approved" if data.approve else "rejected"
    r.admin_note = data.note
    log_action(db, me.id, f"return.{r.status}", "return", r.id, None, {"note": data.note})
    notify_user(db, db.get(User, r.user_id), f"Return {r.return_no} {r.status}",
                data.note or f"Your return request was {r.status}.", kind="order")
    db.commit()
    return r


@router.post("/returns/{return_id}/receive", response_model=ReturnOut)
def receive_return(return_id: int, data: ReceiveIn, db: Session = Depends(get_db), me: User = Depends(returns_staff)):
    """item came back to the warehouse -> restock + refund"""
    r = get_or_404(db, ReturnRequest, return_id, "Return")
    if r.status != "approved":
        raise HTTPException(400, "Return must be approved first")
    get_or_404(db, Warehouse, data.warehouse_id, "Warehouse")
    order = db.query(Order).filter_by(id=r.order_id).with_for_update().first()

    refund_amount = Decimal("0")
    for ri in r.items:
        oi = db.get(OrderItem, ri.order_item_id)
        if data.restock:
            row = stock.get_or_create_row(db, oi.product_id, oi.variant_id, data.warehouse_id)
            stock.add_stock(db, row, ri.quantity, "return", r.return_no, None, me.id)
        # refund what they actually paid for that many units
        refund_amount += money(Decimal(oi.line_total) * ri.quantity / oi.quantity)
        if ri.quantity == oi.quantity:
            oi.fulfillment_status = "returned"

    r.status = "received"
    refund_amount = min(money(refund_amount), order_service.refundable_amount(db, order.id))
    if refund_amount > 0:
        refund = order_service.create_refund(db, order, refund_amount, f"Return {r.return_no}", me.id)
        r.refund_id = refund.id
        if refund.status == "succeeded":
            r.status = "refunded"
    db.commit()
    return r


# ---------------- exchanges ----------------
def _ex_event(db, ex, status, note, user_id):
    ex.status = status
    db.add(ExchangeEvent(exchange_id=ex.id, status=status, note=note, changed_by=user_id))


def _ex_detail(db, ex):
    out = ExchangeDetail.model_validate(ex)
    rows = db.query(ExchangeEvent).filter_by(exchange_id=ex.id).order_by(ExchangeEvent.id).all()
    out.events = [ExchangeEventOut.model_validate(e) for e in rows]
    return out


@router.post("/exchanges", response_model=ExchangeDetail, status_code=201)
def request_exchange(data: ExchangeIn, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    oi = db.get(OrderItem, data.order_item_id)
    order = db.get(Order, oi.order_id) if oi else None
    if not order or order.user_id != user.id:
        raise HTTPException(404, "Order item not found")
    _check_window(db, order)
    left = oi.quantity - _already_returned(db, oi.id)
    if data.quantity > left:
        raise HTTPException(400, f"Only {left} unit(s) can be exchanged")
    variant = db.get(ProductVariant, data.replacement_variant_id)
    if not variant or variant.product_id != oi.product_id or not variant.is_active:
        raise HTTPException(400, "Replacement must be an active variant of the same product")
    if variant.id == oi.variant_id:
        raise HTTPException(400, "Pick a different size/color")
    if stock.total_available(db, oi.product_id, variant.id) < data.quantity:
        raise HTTPException(400, "Replacement is out of stock")

    ex = ExchangeRequest(exchange_no=make_code("EXC"), order_id=order.id, order_item_id=oi.id, user_id=user.id,
                         replacement_variant_id=variant.id, quantity=data.quantity, reason=data.reason)
    db.add(ex)
    db.flush()
    _ex_event(db, ex, "requested", data.reason, user.id)
    db.commit()
    return _ex_detail(db, ex)


@router.get("/exchanges", response_model=Page[ExchangeOut])
def list_exchanges(status: Optional[str] = None, page: int = 1, size: int = 20,
                   user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(ExchangeRequest)
    if user.role_name not in (ADMIN, ORDER_MANAGER, SUPPORT_AGENT, "super_admin"):
        q = q.filter(ExchangeRequest.user_id == user.id)
    if status:
        q = q.filter(ExchangeRequest.status == status)
    return paginate(q.order_by(ExchangeRequest.id.desc()), page, size)


@router.get("/exchanges/{ex_id}", response_model=ExchangeDetail)
def get_exchange(ex_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ex = get_or_404(db, ExchangeRequest, ex_id, "Exchange")
    check_owner(user, ex.user_id, ADMIN, ORDER_MANAGER, SUPPORT_AGENT)
    return _ex_detail(db, ex)


@router.post("/exchanges/{ex_id}/review", response_model=ExchangeDetail)
def review_exchange(ex_id: int, data: ReviewDecisionIn, db: Session = Depends(get_db),
                    me: User = Depends(returns_staff)):
    ex = get_or_404(db, ExchangeRequest, ex_id, "Exchange")
    if ex.status != "requested":
        raise HTTPException(400, f"Exchange is {ex.status}")
    if data.approve:
        oi = db.get(OrderItem, ex.order_item_id)
        row = stock.find_stock_row(db, oi.product_id, ex.replacement_variant_id, ex.quantity, lock=True)
        if not row:
            raise HTTPException(409, "Replacement stock is no longer available")
        stock.reserve(db, row, ex.quantity, ex.exchange_no, me.id)  # hold the replacement
        ex.replacement_inventory_id = row.id
        _ex_event(db, ex, "approved", data.note, me.id)
    else:
        _ex_event(db, ex, "rejected", data.note, me.id)
    notify_user(db, db.get(User, ex.user_id), f"Exchange {ex.exchange_no} {ex.status}",
                data.note or f"Your exchange was {ex.status}.", kind="order")
    db.commit()
    return _ex_detail(db, ex)


@router.post("/exchanges/{ex_id}/receive-item", response_model=ExchangeDetail)
def exchange_received(ex_id: int, data: ReceiveIn, db: Session = Depends(get_db), me: User = Depends(returns_staff)):
    ex = get_or_404(db, ExchangeRequest, ex_id, "Exchange")
    if ex.status != "approved":
        raise HTTPException(400, "Exchange must be approved first")
    oi = db.get(OrderItem, ex.order_item_id)
    if data.restock:
        row = stock.get_or_create_row(db, oi.product_id, oi.variant_id, data.warehouse_id)
        stock.add_stock(db, row, ex.quantity, "return", ex.exchange_no, None, me.id)
    _ex_event(db, ex, "item_received", "Original item received" + ("" if data.restock else " (damaged)"), me.id)
    db.commit()
    return _ex_detail(db, ex)


@router.post("/exchanges/{ex_id}/ship-replacement", response_model=ExchangeDetail)
def ship_replacement(ex_id: int, db: Session = Depends(get_db), me: User = Depends(returns_staff)):
    ex = get_or_404(db, ExchangeRequest, ex_id, "Exchange")
    if ex.status != "item_received":
        raise HTTPException(400, "Receive the original item first")
    row = db.query(Inventory).filter_by(id=ex.replacement_inventory_id).with_for_update().first()
    stock.consume_reserved(db, row, ex.quantity, ex.exchange_no, me.id)
    _ex_event(db, ex, "replacement_shipped", "Replacement dispatched", me.id)
    db.commit()
    return _ex_detail(db, ex)


@router.post("/exchanges/{ex_id}/complete", response_model=ExchangeDetail)
def complete_exchange(ex_id: int, db: Session = Depends(get_db), me: User = Depends(returns_staff)):
    ex = get_or_404(db, ExchangeRequest, ex_id, "Exchange")
    if ex.status != "replacement_shipped":
        raise HTTPException(400, "Replacement not shipped yet")
    _ex_event(db, ex, "completed", "Customer received replacement", me.id)
    notify_user(db, db.get(User, ex.user_id), f"Exchange {ex.exchange_no} completed",
                "Enjoy your replacement!", kind="order")
    db.commit()
    return _ex_detail(db, ex)