from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import now


class ShippingProvider(Base):
    __tablename__ = "shipping_providers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    tracking_url = Column(String(255))
    is_active = Column(Boolean, default=True)


class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    shipment_ref = Column(String(40), unique=True, nullable=False)
    order_id = Column(ForeignKey("orders.id"), nullable=False, index=True)
    provider_id = Column(ForeignKey("shipping_providers.id"))
    tracking_number = Column(String(80), unique=True)
    # created / dispatched / in_transit / out_for_delivery / delivered / exception / returned
    status = Column(String(30), default="created")
    weight_kg = Column(String(20))
    dispatched_at = Column(DateTime)
    delivered_at = Column(DateTime)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=now)

    provider = relationship("ShippingProvider", lazy="joined")


class TrackingEvent(Base):
    __tablename__ = "tracking_events"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(ForeignKey("shipments.id", ondelete="CASCADE"), index=True)
    status = Column(String(30))
    location = Column(String(150))
    description = Column(String(255))
    is_exception = Column(Boolean, default=False)
    source = Column(String(20), default="manual")  # manual / provider
    event_time = Column(DateTime, default=now)


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(ForeignKey("shipments.id", ondelete="CASCADE"), unique=True)
    assigned_to = Column(ForeignKey("users.id"))  # delivery person
    provider_id = Column(ForeignKey("shipping_providers.id"))
    # assigned / out_for_delivery / delivered / failed
    status = Column(String(20), default="assigned")
    attempts = Column(Integer, default=0)
    receiver_name = Column(String(150))
    proof_note = Column(Text)
    delivered_at = Column(DateTime)
    created_at = Column(DateTime, default=now)


class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"
    id = Column(Integer, primary_key=True)
    assignment_id = Column(ForeignKey("delivery_assignments.id", ondelete="CASCADE"), index=True)
    attempt_no = Column(Integer)
    result = Column(String(20))  # delivered / failed
    reason = Column(String(255))
    attempted_by = Column(Integer)
    attempted_at = Column(DateTime, default=now)


class ReturnRequest(Base):
    __tablename__ = "return_requests"
    id = Column(Integer, primary_key=True)
    return_no = Column(String(40), unique=True)
    order_id = Column(ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    reason = Column(String(500))
    # requested / approved / rejected / received / refunded
    status = Column(String(20), default="requested")
    admin_note = Column(String(500))
    refund_id = Column(Integer)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    items = relationship("ReturnItem", lazy="selectin", cascade="all, delete-orphan")


class ReturnItem(Base):
    __tablename__ = "return_items"
    id = Column(Integer, primary_key=True)
    return_id = Column(ForeignKey("return_requests.id", ondelete="CASCADE"))
    order_item_id = Column(ForeignKey("order_items.id"))
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255))


class ExchangeRequest(Base):
    __tablename__ = "exchange_requests"
    id = Column(Integer, primary_key=True)
    exchange_no = Column(String(40), unique=True)
    order_id = Column(ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(ForeignKey("order_items.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    replacement_variant_id = Column(ForeignKey("product_variants.id"))
    replacement_inventory_id = Column(ForeignKey("inventory.id"))
    quantity = Column(Integer, nullable=False)
    reason = Column(String(500))
    # requested / approved / rejected / item_received / replacement_shipped / completed
    status = Column(String(30), default="requested")
    created_at = Column(DateTime, default=now)


class ExchangeEvent(Base):
    __tablename__ = "exchange_events"
    id = Column(Integer, primary_key=True)
    exchange_id = Column(ForeignKey("exchange_requests.id", ondelete="CASCADE"), index=True)
    status = Column(String(30))
    note = Column(String(255))
    changed_by = Column(Integer)
    created_at = Column(DateTime, default=now)