# Module 33 shipping orders, 34 tracking, 35 delivery
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import check_owner, get_current_user, require_roles
from app.models import (DeliveryAssignment, DeliveryAttempt, Order, Shipment, ShippingProvider, TrackingEvent,
                        User)
from app.roles import ADMIN, DELIVERY_MANAGER, ORDER_MANAGER, SUPPORT_AGENT
from app.schemas.common import Page
from app.schemas.logistics import (AssignIn, AssignmentDetail, AssignmentOut, AttemptIn, AttemptOut, ProviderIn,
                                   ProviderOut, ProviderUpdateIn, ShipmentDetail, ShipmentIn, ShipmentOut,
                                   TrackingEventOut, TrackingIn)
from app.services import orders as order_service
from app.services.audit import log_action
from app.services.notify import notify_roles, notify_user
from app.utils import get_or_404, make_code, now, paginate

router = APIRouter(tags=["33. Shipments, 34. Tracking, 35. Delivery"])
ship_staff = require_roles(ADMIN, ORDER_MANAGER, DELIVERY_MANAGER)
MAX_ATTEMPTS = 3


def _detail(db, s):
    out = ShipmentDetail.model_validate(s)
    events = db.query(TrackingEvent).filter_by(shipment_id=s.id).order_by(TrackingEvent.event_time).all()
    out.events = [TrackingEventOut.model_validate(e) for e in events]
    if s.provider and s.provider.tracking_url and s.tracking_number:
        out.tracking_link = s.provider.tracking_url.replace("{tracking}", s.tracking_number)
    return out


def _complete_delivery(db, shipment, user_id):
    shipment.status = "delivered"
    shipment.delivered_at = now()
    order = db.get(Order, shipment.order_id)
    if order.status == "shipped":
        order_service.change_status(db, order, "delivered", user_id, f"Delivered ({shipment.shipment_ref})")


def _add_event(db, shipment, status, location=None, description=None, source="manual", user_id=None):
    is_exc = status == "exception"
    db.add(TrackingEvent(shipment_id=shipment.id, status=status, location=location, description=description,
                         is_exception=is_exc, source=source))
    if status == "delivered":
        _complete_delivery(db, shipment, user_id)
    else:
        shipment.status = status
    if is_exc:
        notify_roles(db, [DELIVERY_MANAGER, SUPPORT_AGENT], "Delivery exception",
                     f"Shipment {shipment.shipment_ref}: {description or 'exception'}", kind="order")
        customer = db.get(User, db.get(Order, shipment.order_id).user_id)
        notify_user(db, customer, "Delivery delayed",
                    f"There is a problem with your shipment {shipment.shipment_ref}. We're on it.", kind="order")


# ---------------- providers ----------------
@router.get("/shipping-providers", response_model=list[ProviderOut])
def list_providers(db: Session = Depends(get_db), _=Depends(ship_staff)):
    return db.query(ShippingProvider).all()


@router.post("/shipping-providers", response_model=ProviderOut, status_code=201)
def add_provider(data: ProviderIn, db: Session = Depends(get_db), _=Depends(require_roles(ADMIN, DELIVERY_MANAGER))):
    if db.query(ShippingProvider).filter_by(code=data.code).first():
        raise HTTPException(409, "Provider code exists")
    p = ShippingProvider(**data.model_dump())
    db.add(p)
    db.commit()
    return p


# ---------------- shipments ----------------
@router.post("/shipments", response_model=ShipmentDetail, status_code=201)
def create_shipment(data: ShipmentIn, db: Session = Depends(get_db), me: User = Depends(ship_staff)):
    order = get_or_404(db, Order, data.order_id, "Order")
    if order.status not in ("confirmed", "processing"):
        raise HTTPException(400, f"Order is {order.status}, it must be confirmed/processing to ship")
    provider = get_or_404(db, ShippingProvider, data.provider_id, "Provider")
    if not provider.is_active:
        raise HTTPException(400, "Provider is inactive")
    active = db.query(Shipment).filter(Shipment.order_id == order.id,
                                       Shipment.status.notin_(["returned", "exception"])).first()
    if active:
        raise HTTPException(409, f"Order already has shipment {active.shipment_ref}")
    tracking = data.tracking_number or f"{provider.code.upper()}{make_code('T', 6).replace('-', '')}"
    if db.query(Shipment).filter_by(tracking_number=tracking).first():
        raise HTTPException(409, "Tracking number already used")
    s = Shipment(shipment_ref=make_code("SHP"), order_id=order.id, provider_id=provider.id,
                 tracking_number=tracking, weight_kg=data.weight_kg, created_by=me.id)
    db.add(s)
    db.flush()
    db.add(TrackingEvent(shipment_id=s.id, status="created", description="Shipment created"))
    if order.status == "confirmed":
        order_service.change_status(db, order, "processing", me.id, "Packing started")
    db.commit()
    db.refresh(s)
    return _detail(db, s)


@router.post("/shipments/{shipment_id}/dispatch", response_model=ShipmentDetail)
def dispatch(shipment_id: int, db: Session = Depends(get_db), me: User = Depends(ship_staff)):
    s = get_or_404(db, Shipment, shipment_id, "Shipment")
    if s.status != "created":
        raise HTTPException(400, f"Shipment already {s.status}")
    order = db.query(Order).filter_by(id=s.order_id).with_for_update().first()
    order_service.change_status(db, order, "shipped", me.id, f"Dispatched via shipment {s.shipment_ref}")
    s.status = "dispatched"
    s.dispatched_at = now()
    db.add(TrackingEvent(shipment_id=s.id, status="dispatched", description="Handed to courier"))
    log_action(db, me.id, "shipment.dispatched", "shipment", s.id, None, {"order": order.order_number})
    db.commit()
    return _detail(db, s)


@router.get("/shipments", response_model=Page[ShipmentOut])
def list_shipments(status: Optional[str] = None, order_id: Optional[int] = None, page: int = 1, size: int = 20,
                   db: Session = Depends(get_db), _=Depends(require_roles(ADMIN, ORDER_MANAGER, DELIVERY_MANAGER,
                                                                         SUPPORT_AGENT))):
    q = db.query(Shipment)
    if status:
        q = q.filter_by(status=status)
    if order_id:
        q = q.filter_by(order_id=order_id)
    return paginate(q.order_by(Shipment.id.desc()), page, size)


@router.get("/shipments/{shipment_id}", response_model=ShipmentDetail)
def shipment_detail(shipment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = get_or_404(db, Shipment, shipment_id, "Shipment")
    order = db.get(Order, s.order_id)
    check_owner(user, order.user_id, ADMIN, ORDER_MANAGER, DELIVERY_MANAGER, SUPPORT_AGENT)
    return _detail(db, s)


@router.get("/orders/{order_id}/shipments", response_model=list[ShipmentDetail])
def order_shipments(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = get_or_404(db, Order, order_id, "Order")
    check_owner(user, order.user_id, ADMIN, ORDER_MANAGER, DELIVERY_MANAGER, SUPPORT_AGENT)
    return [_detail(db, s) for s in db.query(Shipment).filter_by(order_id=order_id).all()]


# ---------------- tracking ----------------
@router.get("/shipments/track/{tracking_number}", response_model=ShipmentDetail)
def track(tracking_number: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.query(Shipment).filter_by(tracking_number=tracking_number).first()
    if not s:
        raise HTTPException(404, "Tracking number not found")
    return shipment_detail(s.id, user, db)


@router.post("/shipments/{shipment_id}/tracking", response_model=ShipmentDetail)
def add_tracking(shipment_id: int, data: TrackingIn, db: Session = Depends(get_db), me: User = Depends(ship_staff)):
    s = get_or_404(db, Shipment, shipment_id, "Shipment")
    if s.status in ("created",):
        raise HTTPException(400, "Dispatch the shipment first")
    if s.status == "delivered":
        raise HTTPException(400, "Shipment already delivered")
    _add_event(db, s, data.status, data.location, data.description, "manual", me.id)
    db.commit()
    return _detail(db, s)


@router.post("/shipments/provider-updates")
def provider_update(data: ProviderUpdateIn, db: Session = Depends(get_db),
                    x_provider_token: Optional[str] = Header(None, alias="X-Provider-Token")):
    """courier companies call this. protected by a shared token from .env"""
    if not x_provider_token or x_provider_token != settings.provider_webhook_token:
        raise HTTPException(401, "Bad provider token")
    s = db.query(Shipment).filter_by(tracking_number=data.tracking_number).first()
    if not s:
        raise HTTPException(404, "Unknown tracking number")
    if s.status == "delivered":
        return {"status": "ignored", "reason": "already delivered"}
    if s.status == "created":
        raise HTTPException(400, "Shipment not dispatched yet")
    _add_event(db, s, data.status, data.location, data.description, "provider")
    db.commit()
    return {"status": "ok", "shipment_status": s.status}


# ---------------- delivery ----------------
@router.post("/shipments/{shipment_id}/assign", response_model=AssignmentOut)
def assign_delivery(shipment_id: int, data: AssignIn, db: Session = Depends(get_db),
                    me: User = Depends(require_roles(ADMIN, DELIVERY_MANAGER))):
    s = get_or_404(db, Shipment, shipment_id, "Shipment")
    if s.status in ("created", "delivered"):
        raise HTTPException(400, f"Can't assign a shipment that is {s.status}")
    if data.assigned_to:
        person = db.get(User, data.assigned_to)
        if not person or person.role_name != DELIVERY_MANAGER or person.status != "active":
            raise HTTPException(400, "assigned_to must be an active delivery staff user")
    if data.provider_id:
        get_or_404(db, ShippingProvider, data.provider_id, "Provider")
    a = db.query(DeliveryAssignment).filter_by(shipment_id=s.id).first()
    if a and a.status == "delivered":
        raise HTTPException(400, "Already delivered")
    if not a:
        a = DeliveryAssignment(shipment_id=s.id)
        db.add(a)
    a.assigned_to = data.assigned_to
    a.provider_id = data.provider_id
    a.status = "assigned"
    db.commit()
    return a


@router.post("/deliveries/{assignment_id}/attempts", response_model=AssignmentDetail)
def record_attempt(assignment_id: int, data: AttemptIn, db: Session = Depends(get_db),
                   me: User = Depends(require_roles(ADMIN, DELIVERY_MANAGER))):
    a = get_or_404(db, DeliveryAssignment, assignment_id, "Delivery")
    if a.status in ("delivered", "failed"):
        raise HTTPException(400, f"Delivery is already {a.status}")
    s = db.get(Shipment, a.shipment_id)
    a.attempts += 1
    db.add(DeliveryAttempt(assignment_id=a.id, attempt_no=a.attempts, result=data.result,
                           reason=data.reason, attempted_by=me.id))
    if data.result == "delivered":
        a.status = "delivered"
        a.receiver_name = data.receiver_name
        a.proof_note = data.proof_note
        a.delivered_at = now()
        db.add(TrackingEvent(shipment_id=s.id, status="delivered", description=f"Received by {data.receiver_name}"))
        _complete_delivery(db, s, me.id)
    else:
        if a.attempts >= MAX_ATTEMPTS:
            a.status = "failed"
            _add_event(db, s, "exception", None, f"Delivery failed after {a.attempts} attempts: {data.reason}",
                       "manual", me.id)
        else:
            a.status = "out_for_delivery"
            db.add(TrackingEvent(shipment_id=s.id, status="out_for_delivery",
                                 description=f"Attempt {a.attempts} failed: {data.reason}"))
            s.status = "out_for_delivery"
    db.commit()
    return delivery_detail(a.id, db, me)


@router.get("/deliveries", response_model=Page[AssignmentOut])
def list_deliveries(status: Optional[str] = None, mine: bool = False, page: int = 1, size: int = 20,
                    db: Session = Depends(get_db), me: User = Depends(require_roles(ADMIN, DELIVERY_MANAGER))):
    q = db.query(DeliveryAssignment)
    if status:
        q = q.filter_by(status=status)
    if mine:
        q = q.filter_by(assigned_to=me.id)
    return paginate(q.order_by(DeliveryAssignment.id.desc()), page, size)


@router.get("/deliveries/{assignment_id}", response_model=AssignmentDetail)
def delivery_detail(assignment_id: int, db: Session = Depends(get_db),
                    _=Depends(require_roles(ADMIN, DELIVERY_MANAGER))):
    a = get_or_404(db, DeliveryAssignment, assignment_id, "Delivery")
    out = AssignmentDetail.model_validate(a)
    rows = db.query(DeliveryAttempt).filter_by(assignment_id=a.id).order_by(DeliveryAttempt.id).all()
    out.attempt_history = [AttemptOut.model_validate(r) for r in rows]
    return out