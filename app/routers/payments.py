# Module 29 payments, Module 30 payment transaction history
import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import check_owner, get_current_user
from app.models import Order, Payment, PaymentEvent, User
from app.roles import ADMIN, FINANCE_MANAGER, ORDER_MANAGER
from app.schemas.common import Page
from app.schemas.payments import IntentOut, PaymentDetail, PaymentEventOut, PaymentOut
from app.services import orders as order_service
from app.services.gateway import SandboxGateway, get_gateway
from app.utils import get_or_404, paginate

router = APIRouter(tags=["29. Payments, 30. Payment History"])


# ---------------- payments ----------------
@router.post("/payments/orders/{order_id}/intent", response_model=IntentOut, status_code=201)
def create_payment(order_id: int, idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
                   user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter_by(id=order_id).with_for_update().first()
    if not order or order.user_id != user.id:
        raise HTTPException(404, "Order not found")
    if order.payment_method != "card":
        raise HTTPException(400, "This order is cash on delivery")
    if order.status == "cancelled":
        raise HTTPException(400, "Order is cancelled")
    if order.payment_status in ("paid", "refunded", "partially_refunded"):
        raise HTTPException(409, "Order is already paid")

    key = f"pay:{user.id}:{idempotency_key or order.id}"
    # one open payment per order - repeat calls get the same one back
    open_payment = db.query(Payment).filter(
        (Payment.idempotency_key == key) | ((Payment.order_id == order.id) & (Payment.status == "pending"))
    ).first()
    if open_payment:
        out = IntentOut.model_validate(open_payment)
        out.is_existing = True
        return out

    gw = get_gateway()
    result = gw.create_intent(order.grand_total, settings.currency, key,
                              {"order_id": str(order.id), "order_number": order.order_number})
    payment = Payment(order_id=order.id, user_id=user.id, amount=order.grand_total, currency=settings.currency,
                      method="card", gateway=gw.name, gateway_ref=result["ref"],
                      client_secret=result["client_secret"], status="pending", idempotency_key=key)
    db.add(payment)
    db.flush()
    db.add(PaymentEvent(payment_id=payment.id, event_type="intent.created", status="pending",
                        payload={"ref": result["ref"]}))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(Payment).filter_by(idempotency_key=key).first()
        out = IntentOut.model_validate(existing)
        out.is_existing = True
        return out
    return IntentOut.model_validate(payment)


def handle_gateway_event(db, event):
    """shared by the real webhook and the sandbox simulator"""
    if db.query(PaymentEvent).filter_by(gateway_event_id=event["id"]).first():
        return {"status": "duplicate_ignored"}
    payment = db.query(Payment).filter_by(gateway_ref=event["ref"]).with_for_update().first()
    if not payment:
        return {"status": "unknown_payment_ignored"}
    db.add(PaymentEvent(payment_id=payment.id, event_type=event["type"], gateway_event_id=event["id"],
                        status="succeeded" if event["type"] == "payment.succeeded" else "failed",
                        payload=event.get("raw")))
    if event["type"] == "payment.succeeded":
        order_service.mark_payment_success(db, payment)
    elif event["type"] == "payment.failed":
        order_service.mark_payment_failed(db, payment, event.get("reason"))
    try:
        db.commit()
    except IntegrityError:
        # same event arrived twice at the same moment
        db.rollback()
        return {"status": "duplicate_ignored"}
    return {"status": "processed", "payment_status": payment.status}


@router.post("/payments/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db),
                          stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
                          sandbox_signature: Optional[str] = Header(None, alias="X-Sandbox-Signature")):
    body = await request.body()
    gw = get_gateway()
    event = gw.parse_webhook(body, stripe_signature if gw.name == "stripe" else sandbox_signature)
    return handle_gateway_event(db, event)


@router.post("/payments/sandbox/{gateway_ref}/simulate")
def simulate_payment(gateway_ref: str, outcome: str = "success", user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    """Pretend to be the card network. Only works with the sandbox gateway."""
    if get_gateway().name != "sandbox":
        raise HTTPException(400, "Simulator is only for sandbox mode")
    payment = db.query(Payment).filter_by(gateway_ref=gateway_ref).first()
    if not payment:
        raise HTTPException(404, "Payment not found")
    check_owner(user, payment.user_id, ADMIN, FINANCE_MANAGER)
    event = {
        "id": "evt_" + uuid.uuid4().hex[:20],
        "type": "payment.succeeded" if outcome == "success" else "payment.failed",
        "data": {"ref": gateway_ref, "reason": None if outcome == "success" else "Card declined (sandbox)"},
    }
    body = json.dumps(event).encode()
    # go through the same signature check as a real webhook
    parsed = SandboxGateway().parse_webhook(body, SandboxGateway.sign(body))
    result = handle_gateway_event(db, parsed)
    result["event_id"] = event["id"]
    result["hint"] = "POST this event again to /payments/webhook with X-Sandbox-Signature to see duplicate protection"
    result["signature"] = SandboxGateway.sign(body)
    result["event"] = event
    result["raw_body"] = body.decode()  # exact bytes that were signed - send these when replaying
    return result


@router.get("/payments", response_model=Page[PaymentOut])
def list_payments(status: Optional[str] = None, order_id: Optional[int] = None, page: int = 1, size: int = 20,
                  user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Payment)
    if user.role_name not in (ADMIN, FINANCE_MANAGER, "super_admin"):
        q = q.filter(Payment.user_id == user.id)
    if status:
        q = q.filter(Payment.status == status)
    if order_id:
        q = q.filter(Payment.order_id == order_id)
    return paginate(q.order_by(Payment.id.desc()), page, size)


@router.get("/payments/{payment_id}", response_model=PaymentDetail)
def payment_detail(payment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = get_or_404(db, Payment, payment_id, "Payment")
    check_owner(user, p.user_id, ADMIN, FINANCE_MANAGER)
    out = PaymentDetail.model_validate(p)
    events = db.query(PaymentEvent).filter_by(payment_id=p.id).order_by(PaymentEvent.id).all()
    out.events = [PaymentEventOut.model_validate(e) for e in events]
    return out


@router.get("/payments/orders/{order_id}/history", response_model=list[PaymentDetail])
def order_payment_history(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = get_or_404(db, Order, order_id, "Order")
    check_owner(user, order.user_id, ADMIN, FINANCE_MANAGER, ORDER_MANAGER)
    return [payment_detail(p.id, user, db) for p in db.query(Payment).filter_by(order_id=order_id).all()]