# Module 24 checkout, 25 orders, 26 order items, 27 order status, 28 cancellation
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import check_owner, get_current_user, is_staff, require_customer, require_roles
from app.models import (Address, CodCollection, CodSetting, Coupon, Order, OrderCancellation, OrderItem,
                        OrderStatusHistory, User)
from app.roles import ADMIN, DELIVERY_MANAGER, FINANCE_MANAGER, ORDER_MANAGER, SUPPORT_AGENT
from app.routers.cart import cart_lines, get_cart, variant_label
from app.schemas.common import Page
from app.schemas.orders import (CancellationOut, CancelIn, CheckoutIn, ItemStatusIn, OrderDetail,
                                OrderItemOut, OrderOut, StatusChangeIn, StatusHistoryOut)
from app.services import orders as order_service
from app.services import stock
from app.services.notify import notify_roles, notify_user
from app.services.pricing import calculate
from app.utils import make_code, money, paginate

router = APIRouter(tags=["24. Checkout, 25-27. Orders, 28. Cancellation"])
ORDER_VIEWERS = (ADMIN, ORDER_MANAGER, SUPPORT_AGENT, FINANCE_MANAGER, DELIVERY_MANAGER)


def _load_order(db, order_id, user):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    check_owner(user, order.user_id, *ORDER_VIEWERS)
    return order


def _detail(db, order):
    history = db.query(OrderStatusHistory).filter_by(order_id=order.id).order_by(OrderStatusHistory.id).all()
    out = OrderDetail.model_validate(order)
    out.history = [StatusHistoryOut.model_validate(h) for h in history]
    return out


def _check_cod(db, summary, lines, address):
    setting = db.query(CodSetting).first()
    if not setting or not setting.is_enabled:
        raise HTTPException(400, "Cash on delivery is not available right now")
    if summary["grand_total"] > money(setting.max_order_amount):
        raise HTTPException(400, f"COD is only allowed for orders up to {setting.max_order_amount}")
    allowed = [c.strip().lower() for c in (setting.allowed_countries or "").split(",") if c.strip()]
    if allowed and address.country.lower() not in allowed:
        raise HTTPException(400, f"COD not available in {address.country}")
    blocked = [p.strip() for p in (setting.blocked_postal_codes or "").split(",") if p.strip()]
    if address.postal_code in blocked:
        raise HTTPException(400, "COD not available for this postal code")
    for product, _, _ in lines:
        if not product.cod_allowed:
            raise HTTPException(400, f"{product.name} can't be paid with cash on delivery")


@router.post("/checkout", response_model=OrderDetail, status_code=201)
def checkout(data: CheckoutIn, response: Response,
             idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
             user: User = Depends(require_customer), db: Session = Depends(get_db)):
    # same key sent twice (double click / retry) -> give back the first order, don't make a new one
    if idempotency_key:
        existing = db.query(Order).filter_by(idempotency_key=f"{user.id}:{idempotency_key}").first()
        if existing:
            response.status_code = 200
            return _detail(db, existing)

    ship_addr = db.get(Address, data.shipping_address_id)
    if not ship_addr or ship_addr.user_id != user.id or ship_addr.is_deleted:
        raise HTTPException(400, "Shipping address not found")
    bill_addr = ship_addr
    if data.billing_address_id:
        bill_addr = db.get(Address, data.billing_address_id)
        if not bill_addr or bill_addr.user_id != user.id or bill_addr.is_deleted:
            raise HTTPException(400, "Billing address not found")

    cart = get_cart(db, user)
    lines = cart_lines(cart)
    coupon_code = data.coupon_code or cart.coupon_code
    summary = calculate(db, lines, coupon_code, data.shipping_method_id, ship_addr.country)
    if data.payment_method == "cod":
        _check_cod(db, summary, lines, ship_addr)

    order = Order(
        order_number=make_code("ORD"), user_id=user.id, status="pending",
        payment_method=data.payment_method,
        payment_status="cod_pending" if data.payment_method == "cod" else "unpaid",
        shipping_address_id=ship_addr.id, billing_address_id=bill_addr.id,
        shipping_address_text=ship_addr.as_text(), billing_address_text=bill_addr.as_text(),
        shipping_method_id=data.shipping_method_id,
        coupon_code=coupon_code.upper() if coupon_code else None,
        subtotal=summary["subtotal"], discount_total=summary["discount_total"], tax_total=summary["tax_total"],
        shipping_total=summary["shipping_total"], grand_total=summary["grand_total"],
        tax_breakdown=summary["tax_breakdown"], notes=data.notes,
        idempotency_key=f"{user.id}:{idempotency_key}" if idempotency_key else None,
    )
    db.add(order)
    db.flush()

    # reserve stock row by row (rows are locked with SELECT FOR UPDATE)
    for line in summary["lines"]:
        product, variant, qty = line["product"], line["variant"], line["quantity"]
        row = stock.find_stock_row(db, product.id, variant.id if variant else None, qty, lock=True)
        if not row:
            db.rollback()
            raise HTTPException(409, f"{product.name} just went out of stock")
        stock.reserve(db, row, qty, order.order_number, user.id)
        order.items.append(OrderItem(
            product_id=product.id, variant_id=variant.id if variant else None, inventory_id=row.id,
            sku=variant.sku if variant else product.sku, product_name=product.name,
            product_description=product.description, variant_label=variant_label(variant) if variant else None,
            unit_price=line["unit_price"], quantity=qty, discount=line["discount"], tax=line["tax"],
            line_total=line["line_total"],
        ))

    if order.coupon_code:
        # atomic bump so two people can't both take the last use
        updated = db.query(Coupon).filter(
            Coupon.code == order.coupon_code,
            (Coupon.usage_limit.is_(None)) | (Coupon.used_count < Coupon.usage_limit),
        ).update({Coupon.used_count: Coupon.used_count + 1}, synchronize_session=False)
        if not updated:
            db.rollback()
            raise HTTPException(409, "Coupon usage limit reached")

    if data.payment_method == "cod":
        db.add(CodCollection(order_id=order.id, expected_amount=order.grand_total))

    db.add(OrderStatusHistory(order_id=order.id, from_status=None, to_status="pending",
                              changed_by=user.id, note="Order placed"))
    cart.items.clear()
    cart.coupon_code = None
    notify_user(db, user, f"Order {order.order_number} placed",
                f"Thanks! Order total {order.grand_total}. "
                + ("Pay on delivery." if data.payment_method == "cod" else "Please complete payment."),
                kind="order", sms=True)
    notify_roles(db, [ORDER_MANAGER], "New order", f"{order.order_number} - {order.grand_total}", kind="order")
    try:
        db.commit()
    except IntegrityError:
        # two requests with the same key raced each other
        db.rollback()
        existing = db.query(Order).filter_by(idempotency_key=f"{user.id}:{idempotency_key}").first()
        if existing:
            response.status_code = 200
            return _detail(db, existing)
        raise
    db.refresh(order)
    return _detail(db, order)


@router.get("/orders", response_model=Page[OrderOut])
def list_orders(status: Optional[str] = None, payment_status: Optional[str] = None,
                order_number: Optional[str] = None, user_id: Optional[int] = None,
                date_from: Optional[date] = None, date_to: Optional[date] = None,
                min_total: Optional[Decimal] = None, max_total: Optional[Decimal] = None,
                page: int = 1, size: int = 20,
                user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Order)
    if not (is_staff(user) and user.role_name in ORDER_VIEWERS + ("super_admin",)):
        q = q.filter(Order.user_id == user.id)  # customers only ever see their own
    elif user_id:
        q = q.filter(Order.user_id == user_id)
    if status:
        q = q.filter(Order.status == status)
    if payment_status:
        q = q.filter(Order.payment_status == payment_status)
    if order_number:
        q = q.filter(Order.order_number.ilike(f"%{order_number}%"))
    if date_from:
        q = q.filter(Order.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        q = q.filter(Order.created_at <= datetime.combine(date_to, time.max))
    if min_total is not None:
        q = q.filter(Order.grand_total >= min_total)
    if max_total is not None:
        q = q.filter(Order.grand_total <= max_total)
    return paginate(q.order_by(Order.id.desc()), page, size)


@router.get("/orders/{order_id}", response_model=OrderDetail)
def get_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _detail(db, _load_order(db, order_id, user))


@router.get("/orders/number/{order_number}", response_model=OrderDetail)
def get_order_by_number(order_number: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter_by(order_number=order_number).first()
    if not order:
        raise HTTPException(404, "Order not found")
    return get_order(order.id, user, db)


@router.get("/orders/{order_id}/items", response_model=list[OrderItemOut])
def order_items(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _load_order(db, order_id, user).items


@router.put("/orders/{order_id}/items/{item_id}/status", response_model=OrderItemOut)
def item_status(order_id: int, item_id: int, data: ItemStatusIn, db: Session = Depends(get_db),
                me: User = Depends(require_roles(ADMIN, ORDER_MANAGER, DELIVERY_MANAGER))):
    order = _load_order(db, order_id, me)
    item = next((i for i in order.items if i.id == item_id), None)
    if not item:
        raise HTTPException(404, "Item not in order")
    if item.fulfillment_status in ("cancelled", "returned"):
        raise HTTPException(400, f"Item is {item.fulfillment_status}")
    flow = ["pending", "packed", "shipped", "delivered"]
    if flow.index(data.fulfillment_status) < flow.index(item.fulfillment_status):
        raise HTTPException(400, "Item status can't go backwards")
    if data.fulfillment_status in ("shipped", "delivered") and order.status not in ("shipped", "delivered"):
        raise HTTPException(400, "Ship the order first (order status endpoint)")
    item.fulfillment_status = data.fulfillment_status
    db.commit()
    return item


@router.put("/orders/{order_id}/status", response_model=OrderDetail)
def update_status(order_id: int, data: StatusChangeIn, db: Session = Depends(get_db),
                  me: User = Depends(require_roles(ADMIN, ORDER_MANAGER, DELIVERY_MANAGER))):
    order = db.query(Order).filter_by(id=order_id).with_for_update().first()
    if not order:
        raise HTTPException(404, "Order not found")
    # delivery manager only handles the last mile
    if me.role_name == DELIVERY_MANAGER and data.status not in ("shipped", "delivered"):
        raise HTTPException(403, "Delivery manager can only mark shipped / delivered")
    order_service.change_status(db, order, data.status, me.id, data.note)
    db.commit()
    return _detail(db, order)


@router.get("/orders/{order_id}/history", response_model=list[StatusHistoryOut])
def order_history(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _load_order(db, order_id, user)
    return db.query(OrderStatusHistory).filter_by(order_id=order_id).order_by(OrderStatusHistory.id).all()


@router.post("/orders/{order_id}/cancel", response_model=OrderDetail)
def cancel(order_id: int, data: CancelIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter_by(id=order_id).with_for_update().first()
    if not order:
        raise HTTPException(404, "Order not found")
    staff_ok = user.role_name in (ADMIN, ORDER_MANAGER, "super_admin")
    if order.user_id != user.id and not staff_ok:
        raise HTTPException(404, "Order not found")
    order_service.cancel_order(db, order, user, data.reason, is_staff=staff_ok and order.user_id != user.id)
    db.commit()
    return _detail(db, order)


@router.get("/orders/{order_id}/cancellation", response_model=CancellationOut)
def cancellation_info(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _load_order(db, order_id, user)
    row = db.query(OrderCancellation).filter_by(order_id=order_id).first()
    if not row:
        raise HTTPException(404, "Order was not cancelled")
    return row