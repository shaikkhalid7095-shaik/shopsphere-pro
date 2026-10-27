# Module 40 customer support tickets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, is_staff, require_roles
from app.models import Order, Product, Ticket, TicketMessage, User
from app.roles import ADMIN, SUPPORT_AGENT
from app.schemas.common import Page
from app.schemas.engagement import (TicketAssignIn, TicketDetail, TicketIn, TicketMessageIn, TicketOut,
                                    TicketUpdateIn)
from app.services.notify import notify_user
from app.utils import get_or_404, make_code, now, paginate

router = APIRouter(prefix="/tickets", tags=["40. Support Tickets"])
agents = require_roles(ADMIN, SUPPORT_AGENT)


def _can_see(user, ticket):
    if user.role_name in (ADMIN, SUPPORT_AGENT, "super_admin"):
        return True
    return ticket.user_id == user.id


def _detail(ticket, user):
    out = TicketDetail.model_validate(ticket)
    if not is_staff(user):
        out.messages = [m for m in out.messages if not m.is_internal]
    return out


@router.post("", response_model=TicketDetail, status_code=201)
def open_ticket(data: TicketIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.order_id:
        order = db.get(Order, data.order_id)
        if not order or order.user_id != user.id:
            raise HTTPException(400, "Order not found")
    if data.product_id:
        get_or_404(db, Product, data.product_id, "Product")
    t = Ticket(ticket_no=make_code("TKT"), user_id=user.id, order_id=data.order_id, product_id=data.product_id,
               subject=data.subject, priority=data.priority)
    t.messages.append(TicketMessage(sender_id=user.id, message=data.message))
    db.add(t)
    notify_user(db, user, f"Ticket {t.ticket_no} opened", "Our support team will get back to you soon.",
                kind="general", email=True)
    db.commit()
    return _detail(t, user)


@router.get("", response_model=Page[TicketOut])
def list_tickets(status: Optional[str] = None, priority: Optional[str] = None, assigned_to_me: bool = False,
                 page: int = 1, size: int = 20, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Ticket)
    if user.role_name not in (ADMIN, SUPPORT_AGENT, "super_admin"):
        q = q.filter(Ticket.user_id == user.id)
    elif assigned_to_me:
        q = q.filter(Ticket.assigned_to == user.id)
    if status:
        q = q.filter(Ticket.status == status)
    if priority:
        q = q.filter(Ticket.priority == priority)
    return paginate(q.order_by(Ticket.id.desc()), page, size)


@router.get("/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = get_or_404(db, Ticket, ticket_id, "Ticket")
    if not _can_see(user, t):
        raise HTTPException(404, "Ticket not found")
    return _detail(t, user)


@router.post("/{ticket_id}/messages", response_model=TicketDetail)
def reply(ticket_id: int, data: TicketMessageIn, user: User = Depends(get_current_user),
          db: Session = Depends(get_db)):
    t = get_or_404(db, Ticket, ticket_id, "Ticket")
    if not _can_see(user, t):
        raise HTTPException(404, "Ticket not found")
    if t.status == "closed":
        raise HTTPException(400, "Ticket is closed, open a new one")
    internal = data.is_internal and is_staff(user)
    t.messages.append(TicketMessage(sender_id=user.id, message=data.message, is_internal=internal))
    if is_staff(user):
        if t.status == "open":
            t.status = "in_progress"
        if not internal:
            notify_user(db, db.get(User, t.user_id), f"New reply on {t.ticket_no}", data.message[:200], kind="general")
    elif t.status == "resolved":
        t.status = "open"  # customer replied, reopen
    db.commit()
    db.refresh(t)
    return _detail(t, user)


@router.put("/{ticket_id}/assign", response_model=TicketOut)
def assign(ticket_id: int, data: TicketAssignIn, db: Session = Depends(get_db), me: User = Depends(agents)):
    t = get_or_404(db, Ticket, ticket_id, "Ticket")
    agent = db.get(User, data.agent_id)
    if not agent or agent.role_name not in (SUPPORT_AGENT, ADMIN) or agent.status != "active":
        raise HTTPException(400, "Can only assign to an active support agent")
    t.assigned_to = agent.id
    if t.status == "open":
        t.status = "in_progress"
    t.messages.append(TicketMessage(sender_id=me.id, message=f"Assigned to {agent.full_name}", is_internal=True))
    db.commit()
    return t


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, data: TicketUpdateIn, db: Session = Depends(get_db), me: User = Depends(agents)):
    t = get_or_404(db, Ticket, ticket_id, "Ticket")
    changes = data.model_dump(exclude_unset=True)
    if changes.get("status") in ("resolved", "closed") and not (changes.get("resolution") or t.resolution):
        raise HTTPException(400, "Add a resolution before resolving")
    for k, v in changes.items():
        setattr(t, k, v)
    if t.status in ("resolved", "closed") and not t.resolved_at:
        t.resolved_at = now()
        notify_user(db, db.get(User, t.user_id), f"Ticket {t.ticket_no} {t.status}", t.resolution or "", kind="general")
    db.commit()
    return t