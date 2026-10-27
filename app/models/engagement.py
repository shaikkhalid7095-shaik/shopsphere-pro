from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import now


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("product_id", "user_id", name="uq_one_review"),)
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(ForeignKey("orders.id"))
    rating = Column(Integer, nullable=False)
    title = Column(String(150))
    comment = Column(Text)
    status = Column(String(20), default="published")  # published / hidden / removed
    moderated_by = Column(Integer)
    created_at = Column(DateTime, default=now)


class Question(Base):
    __tablename__ = "product_questions"
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(1000), nullable=False)
    status = Column(String(20), default="open")  # open / answered / hidden
    created_at = Column(DateTime, default=now)

    answers = relationship("Answer", lazy="selectin", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "product_answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(ForeignKey("product_questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    text = Column(String(2000), nullable=False)
    status = Column(String(20), default="visible")  # visible / hidden
    created_at = Column(DateTime, default=now)


class Ticket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True)
    ticket_no = Column(String(40), unique=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(ForeignKey("orders.id"))
    product_id = Column(ForeignKey("products.id"))
    subject = Column(String(200), nullable=False)
    # open / in_progress / resolved / closed
    status = Column(String(20), default="open")
    priority = Column(String(10), default="medium")  # low / medium / high / urgent
    assigned_to = Column(ForeignKey("users.id"))
    resolution = Column(Text)
    created_at = Column(DateTime, default=now)
    resolved_at = Column(DateTime)

    messages = relationship("TicketMessage", lazy="selectin", cascade="all, delete-orphan")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(ForeignKey("support_tickets.id", ondelete="CASCADE"))
    sender_id = Column(ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # staff only notes
    created_at = Column(DateTime, default=now)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String(150))
    message = Column(String(1000))
    kind = Column(String(30), default="general")  # order / payment / refund / inventory / general
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)


class MessageProvider(Base):
    __tablename__ = "message_providers"
    id = Column(Integer, primary_key=True)
    channel = Column(String(10), nullable=False)  # email / sms
    name = Column(String(50), nullable=False)  # console / smtp / twilio...
    config = Column(JSON)
    is_active = Column(Boolean, default=True)


class OutboundMessage(Base):
    __tablename__ = "outbound_messages"
    id = Column(Integer, primary_key=True)
    channel = Column(String(10), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(200))
    body = Column(Text)
    template = Column(String(50))
    status = Column(String(20), default="queued")  # queued / sent / failed
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    last_error = Column(String(500))
    created_at = Column(DateTime, default=now)
    sent_at = Column(DateTime)