import logging
import smtplib
from email.message import EmailMessage

from app.config import settings
from app.models import MessageProvider, Notification, OutboundMessage, Role, User
from app.utils import now

log = logging.getLogger("shopsphere.notify")


def notify_user(db, user, title, message, kind="general", email=True, sms=False):
    db.add(Notification(user_id=user.id, title=title, message=message, kind=kind))
    if email:
        queue_message(db, "email", user.email, title, message, template=kind)
    if sms and user.phone:
        queue_message(db, "sms", user.phone, None, f"{title}: {message}", template=kind)


def notify_roles(db, role_names, title, message, kind="general"):
    staff = db.query(User).join(Role).filter(Role.name.in_(role_names), User.status == "active").all()
    for person in staff:
        db.add(Notification(user_id=person.id, title=title, message=message, kind=kind))


def queue_message(db, channel, recipient, subject, body, template=None):
    msg = OutboundMessage(channel=channel, recipient=recipient, subject=subject, body=body, template=template)
    db.add(msg)
    return msg


def _active_provider(db, channel):
    row = db.query(MessageProvider).filter_by(channel=channel, is_active=True).first()
    if row:
        return row.name, (row.config or {})
    name = settings.email_provider if channel == "email" else settings.sms_provider
    return name, {}


def send_one(db, msg: OutboundMessage):
    provider, config = _active_provider(db, msg.channel)
    msg.attempts += 1
    try:
        if provider == "console":
            log.info("[%s -> %s] %s | %s", msg.channel, msg.recipient, msg.subject, msg.body)
            print(f"[{msg.channel.upper()}] to={msg.recipient} subject={msg.subject} body={msg.body}")
        elif provider == "smtp" and msg.channel == "email":
            host = config.get("host") or settings.smtp_host
            port = int(config.get("port") or settings.smtp_port)
            mail = EmailMessage()
            mail["From"] = config.get("from") or settings.smtp_from
            mail["To"] = msg.recipient
            mail["Subject"] = msg.subject or "ShopSphere"
            mail.set_content(msg.body or "")
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.starttls()
                server.login(config.get("user") or settings.smtp_user, config.get("password") or settings.smtp_password)
                server.send_message(mail)
        elif provider == "fail":
            # handy for testing the retry logic
            raise RuntimeError("provider configured to fail")
        else:
            raise RuntimeError(f"Unknown provider '{provider}' for {msg.channel}")
        msg.status = "sent"
        msg.sent_at = now()
        msg.last_error = None
    except Exception as exc:
        msg.last_error = str(exc)[:500]
        msg.status = "failed" if msg.attempts >= msg.max_attempts else "queued"


def process_outbox(db, limit=50):
    pending = (db.query(OutboundMessage)
               .filter(OutboundMessage.status == "queued")
               .order_by(OutboundMessage.id).limit(limit).all())
    for msg in pending:
        send_one(db, msg)
    db.commit()
    return len(pending)