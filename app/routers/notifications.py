# Module 41 in-app notifications, Module 42 email & SMS
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import MessageProvider, Notification, OutboundMessage, User
from app.roles import ADMIN
from app.schemas.common import Message, Page
from app.schemas.engagement import NotificationOut, OutboundOut, ProviderIn, ProviderOut, SendTestIn
from app.services.notify import process_outbox, queue_message, send_one
from app.utils import get_or_404, paginate

router = APIRouter(tags=["41. Notifications, 42. Email & SMS"])
admin = require_roles(ADMIN)


@router.get("/notifications", response_model=Page[NotificationOut])
def my_notifications(unread_only: bool = False, page: int = 1, size: int = 20,
                     user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Notification).filter_by(user_id=user.id)
    if unread_only:
        q = q.filter_by(is_read=False)
    return paginate(q.order_by(Notification.id.desc()), page, size)


@router.get("/notifications/unread-count")
def unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"unread": db.query(Notification).filter_by(user_id=user.id, is_read=False).count()}


@router.put("/notifications/{notif_id}/read", response_model=NotificationOut)
def mark_read(notif_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, notif_id)
    if not n or n.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    db.commit()
    return n


@router.put("/notifications/read-all", response_model=Message)
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.commit()
    return {"message": f"{count} notifications marked read"}


# ---------------- email / sms ----------------
@router.get("/messaging/providers", response_model=list[ProviderOut])
def list_providers(db: Session = Depends(get_db), _=Depends(admin)):
    return db.query(MessageProvider).all()


@router.post("/messaging/providers", response_model=ProviderOut, status_code=201)
def set_provider(data: ProviderIn, db: Session = Depends(get_db), _=Depends(admin)):
    if data.is_active:
        # only one active provider per channel
        db.query(MessageProvider).filter_by(channel=data.channel).update({"is_active": False})
    p = MessageProvider(**data.model_dump())
    db.add(p)
    db.commit()
    return p


@router.get("/messaging/outbox", response_model=Page[OutboundOut])
def outbox(status: Optional[str] = None, channel: Optional[str] = None, page: int = 1, size: int = 50,
           db: Session = Depends(get_db), _=Depends(admin)):
    q = db.query(OutboundMessage)
    if status:
        q = q.filter_by(status=status)
    if channel:
        q = q.filter_by(channel=channel)
    return paginate(q.order_by(OutboundMessage.id.desc()), page, size)


@router.post("/messaging/send-test", response_model=OutboundOut)
def send_test(data: SendTestIn, db: Session = Depends(get_db), _=Depends(admin)):
    msg = queue_message(db, data.channel, data.recipient, data.subject, data.body, template="test")
    db.flush()
    send_one(db, msg)
    db.commit()
    return msg


@router.post("/messaging/process")
def process_now(db: Session = Depends(get_db), _=Depends(admin)):
    return {"processed": process_outbox(db)}


@router.post("/messaging/{msg_id}/retry", response_model=OutboundOut)
def retry_message(msg_id: int, db: Session = Depends(get_db), _=Depends(admin)):
    msg = get_or_404(db, OutboundMessage, msg_id, "Message")
    if msg.status == "sent":
        raise HTTPException(400, "Already sent")
    # manual retry gives it a few more tries
    msg.max_attempts = msg.attempts + 3
    msg.status = "queued"
    send_one(db, msg)
    db.commit()
    return msg