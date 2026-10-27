# Module 31 refunds, Module 32 cash on delivery
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import check_owner, get_current_user, require_roles
from app.models import CodCollection, CodSetting, Order, Payment, Refund, User
from app.roles import ADMIN, DELIVERY_MANAGER, FINANCE_MANAGER
from app.schemas.common import Page
from app.schemas.payments import CodCollectIn, CodOut, CodReconcileIn, CodSettingIn, CodSettingOut, RefundIn, RefundOut
from app.services import orders as order_service
from app.services.audit import log_action
from app.utils import get_or_404, money, now, paginate

router = APIRouter(tags=["31. Refunds, 32. Cash on Delivery"])
finance = require_roles(ADMIN, FINANCE_MANAGER)


# ---------------- refunds ----------------
@router.post("/refunds", response_model=RefundOut, status_code=201)
def create_refund(data: RefundIn, db: Session = Depends(get_db), me: User = Depends(finance)):
    order = db.query(Order).filter_by(id=data.order_id).with_for_update().first()
    if not order:
        raise HTTPException(404, "Order not found")
    refund = order_service.create_refund(db, order, data.amount, data.reason, me.id, process_now=data.process_now)
    db.commit()
    return refund


@router.post("/refunds/{refund_id}/process", response_model=RefundOut)
def process_refund(refund_id: int, db: Session = Depends(get_db), me: User = Depends(finance)):
    refund = db.query(Refund).filter_by(id=refund_id).with_for_update().first()
    if not refund:
        raise HTTPException(404, "Refund not found")
    order_service.process_refund(db, refund, me.id)
    db.commit()
    return refund


@router.post("/refunds/{refund_id}/reject", response_model=RefundOut)
def reject_refund(refund_id: int, db: Session = Depends(get_db), me: User = Depends(finance)):
    refund = get_or_404(db, Refund, refund_id, "Refund")
    if refund.status != "requested":
        raise HTTPException(400, f"Refund is {refund.status}")
    refund.status = "rejected"
    refund.processed_by = me.id
    refund.processed_at = now()
    log_action(db, me.id, "refund.rejected", "refund", refund.id, None, None)
    db.commit()
    return refund


@router.get("/refunds", response_model=Page[RefundOut])
def list_refunds(status: Optional[str] = None, order_id: Optional[int] = None, page: int = 1, size: int = 20,
                 user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Refund)
    if user.role_name not in (ADMIN, FINANCE_MANAGER, "super_admin"):
        q = q.join(Order, Order.id == Refund.order_id).filter(Order.user_id == user.id)
    if status:
        q = q.filter(Refund.status == status)
    if order_id:
        q = q.filter(Refund.order_id == order_id)
    return paginate(q.order_by(Refund.id.desc()), page, size)


@router.get("/refunds/{refund_id}", response_model=RefundOut)
def refund_detail(refund_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = get_or_404(db, Refund, refund_id, "Refund")
    order = db.get(Order, r.order_id)
    check_owner(user, order.user_id, ADMIN, FINANCE_MANAGER)
    return r


@router.get("/refunds/orders/{order_id}/refundable")
def refundable(order_id: int, db: Session = Depends(get_db), _=Depends(finance)):
    get_or_404(db, Order, order_id, "Order")
    return {"order_id": order_id, "paid": order_service.paid_amount(db, order_id),
            "refunded_or_pending": order_service.refunded_amount(db, order_id),
            "refundable": order_service.refundable_amount(db, order_id)}


# ---------------- COD ----------------
def _cod_setting(db):
    s = db.query(CodSetting).first()
    if not s:
        s = CodSetting()
        db.add(s)
        db.flush()
    return s


@router.get("/cod/settings", response_model=CodSettingOut)
def get_cod_settings(db: Session = Depends(get_db)):
    s = _cod_setting(db)
    db.commit()
    return s


@router.put("/cod/settings", response_model=CodSettingOut)
def update_cod_settings(data: CodSettingIn, db: Session = Depends(get_db), me: User = Depends(finance)):
    s = _cod_setting(db)
    for k, v in data.model_dump().items():
        setattr(s, k, v)
    log_action(db, me.id, "cod.settings", "cod_settings", s.id, None, data.model_dump())
    db.commit()
    return s


@router.get("/cod/collections", response_model=Page[CodOut])
def list_cod(status: Optional[str] = None, page: int = 1, size: int = 20, db: Session = Depends(get_db),
             _=Depends(require_roles(ADMIN, FINANCE_MANAGER, DELIVERY_MANAGER))):
    q = db.query(CodCollection)
    if status:
        q = q.filter_by(status=status)
    return paginate(q.order_by(CodCollection.id.desc()), page, size)


@router.post("/cod/collections/{order_id}/collect", response_model=CodOut)
def collect_cod(order_id: int, data: CodCollectIn, db: Session = Depends(get_db),
                me: User = Depends(require_roles(ADMIN, DELIVERY_MANAGER))):
    row = db.query(CodCollection).filter_by(order_id=order_id).with_for_update().first()
    if not row:
        raise HTTPException(404, "No COD record for this order")
    if row.status != "pending":
        raise HTTPException(409, f"COD already {row.status}")
    order = db.get(Order, order_id)
    if order.status not in ("shipped", "delivered"):
        raise HTTPException(400, "Can only collect cash after the order is shipped")

    row.collected_amount = money(data.amount)
    row.collected_by = me.id
    row.collected_at = now()
    row.note = data.note
    row.status = "collected" if money(data.amount) == money(row.expected_amount) else "mismatch"

    if data.amount > 0:
        db.add(Payment(order_id=order.id, user_id=order.user_id, amount=money(data.amount),
                       currency=settings.currency, method="cod", gateway="cod",
                       gateway_ref=f"cod_{order.order_number}", status="succeeded",
                       idempotency_key=f"cod:{order.id}"))
        order.payment_status = "paid"
    log_action(db, me.id, "cod.collected", "order", order.id, None,
               {"collected": data.amount, "expected": row.expected_amount, "status": row.status})
    db.commit()
    return row


@router.post("/cod/collections/{order_id}/reconcile", response_model=CodOut)
def reconcile_cod(order_id: int, data: CodReconcileIn, db: Session = Depends(get_db), me: User = Depends(finance)):
    row = db.query(CodCollection).filter_by(order_id=order_id).first()
    if not row:
        raise HTTPException(404, "No COD record for this order")
    if row.status not in ("collected", "mismatch"):
        raise HTTPException(400, f"Can't reconcile, status is {row.status}")
    if row.status == "mismatch" and not data.note:
        raise HTTPException(400, "A note is required to reconcile a mismatch")
    row.status = "reconciled"
    row.reconciled_by = me.id
    row.reconciled_at = now()
    if data.note:
        row.note = f"{row.note or ''} | {data.note}".strip(" |")
    log_action(db, me.id, "cod.reconciled", "order", order_id, None, {"note": data.note})
    db.commit()
    return row