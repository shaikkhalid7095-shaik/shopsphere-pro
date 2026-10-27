from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func

from app.models import (CodCollection, Inventory, Order, OrderCancellation, OrderStatusHistory, Payment,
                        Refund, User)
from app.services import stock
from app.services.audit import log_action
from app.services.gateway import gateway_for
from app.services.notify import notify_user
from app.utils import make_code, money, now

# which status can move to which
TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": [],
}


def can_move(current, new):
    return new in TRANSITIONS.get(current, [])


def change_status(db, order: Order, new_status: str, user_id=None, note=None):
    if order.status == new_status:
        return order
    if not can_move(order.status, new_status):
        raise HTTPException(400, f"Cannot move order from '{order.status}' to '{new_status}'")
    if new_status == "cancelled":
        raise HTTPException(400, "Use the cancel endpoint to cancel an order")
    paid_ok = order.payment_status in ("paid", "partially_refunded")
    if new_status in ("processing", "shipped") and order.payment_method == "card" and not paid_ok:
        raise HTTPException(400, "Card order is not paid yet")

    old = order.status
    if new_status == "shipped":
        for item in order.items:
            if item.inventory_id and item.fulfillment_status not in ("cancelled", "shipped"):
                row = db.query(Inventory).filter_by(id=item.inventory_id).with_for_update().first()
                stock.consume_reserved(db, row, item.quantity, order.order_number, user_id)
            if item.fulfillment_status != "cancelled":
                item.fulfillment_status = "shipped"
    if new_status == "processing":
        for item in order.items:
            if item.fulfillment_status == "pending":
                item.fulfillment_status = "packed"
    if new_status == "delivered":
        for item in order.items:
            if item.fulfillment_status == "shipped":
                item.fulfillment_status = "delivered"

    order.status = new_status
    db.add(OrderStatusHistory(order_id=order.id, from_status=old, to_status=new_status, changed_by=user_id, note=note))
    log_action(db, user_id, "order.status_change", "order", order.id, {"status": old}, {"status": new_status})

    customer = db.get(User, order.user_id)
    notify_user(db, customer, f"Order {order.order_number} {new_status}",
                f"Your order {order.order_number} is now {new_status}.", kind="order")
    return order


def paid_amount(db, order_id) -> Decimal:
    total = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.order_id == order_id, Payment.status == "succeeded").scalar()
    return money(total)


def refunded_amount(db, order_id) -> Decimal:
    total = db.query(func.coalesce(func.sum(Refund.amount), 0)).filter(
        Refund.order_id == order_id, Refund.status.in_(["requested", "processing", "succeeded"])).scalar()
    return money(total)


def refundable_amount(db, order_id) -> Decimal:
    return money(paid_amount(db, order_id) - refunded_amount(db, order_id))


def create_refund(db, order: Order, amount, reason, user_id, process_now=True):
    amount = money(amount)
    if amount <= 0:
        raise HTTPException(400, "Refund amount must be positive")
    available = refundable_amount(db, order.id)
    if amount > available:
        raise HTTPException(400, f"Refund exceeds refundable amount ({available})")

    payment = (db.query(Payment)
               .filter(Payment.order_id == order.id, Payment.status == "succeeded")
               .order_by(Payment.id.desc()).first())
    refund = Refund(refund_no=make_code("RF"), payment_id=payment.id if payment else None, order_id=order.id,
                    amount=amount, reason=reason, status="requested", requested_by=user_id)
    db.add(refund)
    db.flush()
    if process_now:
        process_refund(db, refund, user_id)
    return refund


def process_refund(db, refund: Refund, user_id):
    if refund.status not in ("requested", "failed"):
        raise HTTPException(400, f"Refund is already {refund.status}")
    payment = db.get(Payment, refund.payment_id) if refund.payment_id else None
    if not payment:
        raise HTTPException(400, "No successful payment found to refund")
    refund.status = "processing"
    try:
        result = gateway_for(payment.gateway).refund(payment.gateway_ref, refund.amount)
        refund.gateway_ref = result["ref"]
        refund.status = result["status"]
    except HTTPException:
        raise
    except Exception as exc:
        refund.status = "failed"
        log_action(db, user_id, "refund.failed", "refund", refund.id, None, {"error": str(exc)})
        return refund

    refund.processed_by = user_id
    refund.processed_at = now()
    order = db.get(Order, refund.order_id)
    if refund.status == "succeeded":
        left = refundable_amount(db, order.id)
        order.payment_status = "refunded" if left <= 0 else "partially_refunded"
    log_action(db, user_id, "refund.processed", "refund", refund.id, None,
               {"status": refund.status, "amount": refund.amount})
    customer = db.get(User, order.user_id)
    notify_user(db, customer, "Refund update",
                f"Refund {refund.refund_no} of {refund.amount} for order {order.order_number} is {refund.status}.",
                kind="refund")
    return refund


def cancel_order(db, order: Order, user, reason: str, is_staff=False):
    if order.status == "cancelled":
        raise HTTPException(409, "Order is already cancelled")
    allowed = ["pending", "confirmed", "processing"] if is_staff else ["pending", "confirmed"]
    if order.status not in allowed:
        raise HTTPException(400, f"Order in '{order.status}' status cannot be cancelled")

    # give the reserved stock back
    for item in order.items:
        if item.inventory_id and item.fulfillment_status in ("pending", "packed"):
            row = db.query(Inventory).filter_by(id=item.inventory_id).with_for_update().first()
            stock.release(db, row, item.quantity, order.order_number, user.id)
        item.fulfillment_status = "cancelled"

    old = order.status
    order.status = "cancelled"
    db.add(OrderStatusHistory(order_id=order.id, from_status=old, to_status="cancelled",
                              changed_by=user.id, note=reason))

    # stop any pending card payments so they can't succeed later
    for p in db.query(Payment).filter_by(order_id=order.id, status="pending").all():
        p.status = "cancelled"

    cod = db.query(CodCollection).filter_by(order_id=order.id).first()
    if cod and cod.status == "pending":
        cod.status = "cancelled"

    refund = None
    outcome = "Cancelled, no payment taken"
    if refundable_amount(db, order.id) > 0:
        refund = create_refund(db, order, refundable_amount(db, order.id), "Order cancelled", user.id)
        outcome = f"Cancelled, refund {refund.refund_no} {refund.status}"

    db.add(OrderCancellation(order_id=order.id, requested_by=user.id, reason=reason,
                             outcome=outcome, refund_id=refund.id if refund else None))
    log_action(db, user.id, "order.cancelled", "order", order.id, {"status": old},
               {"status": "cancelled", "reason": reason})
    customer = db.get(User, order.user_id)
    notify_user(db, customer, f"Order {order.order_number} cancelled", outcome, kind="order")
    return outcome


def mark_payment_success(db, payment: Payment, event_payload=None):
    if payment.status == "succeeded":
        return  # already done, webhooks can repeat
    order = db.get(Order, payment.order_id)
    payment.status = "succeeded"
    if order.status == "cancelled":
        # money came in for a cancelled order -> give it straight back
        order.payment_status = "paid"
        create_refund(db, order, payment.amount, "Payment received after cancellation", None)
        return
    order.payment_status = "paid"
    if order.status == "pending":
        change_status(db, order, "confirmed", None, "Payment received")
    customer = db.get(User, order.user_id)
    notify_user(db, customer, "Payment successful",
                f"We received {payment.amount} {payment.currency} for order {order.order_number}.", kind="payment")


def mark_payment_failed(db, payment: Payment, reason=None):
    if payment.status in ("succeeded", "failed"):
        return
    payment.status = "failed"
    payment.failure_reason = reason
    order = db.get(Order, payment.order_id)
    if order.payment_status != "paid":
        order.payment_status = "failed"
    customer = db.get(User, order.user_id)
    notify_user(db, customer, "Payment failed",
                f"Payment for order {order.order_number} failed. {reason or ''}".strip(), kind="payment")