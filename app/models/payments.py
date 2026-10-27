from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String

from app.database import Base
from app.utils import now


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(5), default="INR")
    method = Column(String(10), default="card")  # card / cod
    gateway = Column(String(20))  # stripe / sandbox / cod
    gateway_ref = Column(String(120), unique=True)
    client_secret = Column(String(255))
    # pending / succeeded / failed / cancelled
    status = Column(String(20), default="pending", index=True)
    idempotency_key = Column(String(80), unique=True)
    failure_reason = Column(String(255))
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)


class PaymentEvent(Base):
    # every attempt / callback is kept here -> transaction history + audit
    __tablename__ = "payment_events"
    id = Column(Integer, primary_key=True)
    payment_id = Column(ForeignKey("payments.id", ondelete="CASCADE"), index=True)
    event_type = Column(String(50))
    status = Column(String(20))
    gateway_event_id = Column(String(120), unique=True)  # stops double processing of webhooks
    payload = Column(JSON)
    created_at = Column(DateTime, default=now)


class Refund(Base):
    __tablename__ = "refunds"
    id = Column(Integer, primary_key=True)
    refund_no = Column(String(40), unique=True)
    payment_id = Column(ForeignKey("payments.id"))
    order_id = Column(ForeignKey("orders.id"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String(255))
    # requested / processing / succeeded / failed / rejected
    status = Column(String(20), default="requested")
    gateway_ref = Column(String(120))
    requested_by = Column(Integer)
    processed_by = Column(Integer)
    created_at = Column(DateTime, default=now)
    processed_at = Column(DateTime)


class CodSetting(Base):
    __tablename__ = "cod_settings"
    id = Column(Integer, primary_key=True)
    is_enabled = Column(Boolean, default=True)
    max_order_amount = Column(Numeric(12, 2), default=10000)
    allowed_countries = Column(String(255), default="India")
    blocked_postal_codes = Column(String(1000), default="")


class CodCollection(Base):
    __tablename__ = "cod_collections"
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey("orders.id"), unique=True, nullable=False)
    expected_amount = Column(Numeric(12, 2), nullable=False)
    collected_amount = Column(Numeric(12, 2))
    # pending / collected / reconciled / mismatch
    status = Column(String(20), default="pending")
    collected_by = Column(Integer)
    collected_at = Column(DateTime)
    reconciled_by = Column(Integer)
    reconciled_at = Column(DateTime)
    note = Column(String(255))