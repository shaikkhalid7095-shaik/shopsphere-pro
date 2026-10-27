from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import now


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    city = Column(String(100))
    capacity = Column(Integer, default=10000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("product_id", "variant_id", "warehouse_id", name="uq_stock_row"),
        CheckConstraint("quantity >= 0", name="ck_qty_positive"),
        CheckConstraint("reserved >= 0", name="ck_reserved_positive"),
    )
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=True)
    warehouse_id = Column(ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)  # physically on hand
    reserved = Column(Integer, default=0, nullable=False)  # held for orders
    min_threshold = Column(Integer, default=5)
    updated_at = Column(DateTime, default=now, onupdate=now)

    warehouse = relationship("Warehouse", lazy="joined")

    @property
    def available(self):
        return self.quantity - self.reserved


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    inventory_id = Column(ForeignKey("inventory.id", ondelete="CASCADE"), index=True)
    change = Column(Integer, nullable=False)
    # add / remove / reserve / release / sale / transfer_out / transfer_in / return / po_receipt
    movement_type = Column(String(30), nullable=False)
    reference = Column(String(100))
    note = Column(String(255))
    created_by = Column(Integer)
    created_at = Column(DateTime, default=now)


class StockTransfer(Base):
    __tablename__ = "stock_transfers"
    id = Column(Integer, primary_key=True)
    transfer_no = Column(String(40), unique=True)
    from_warehouse_id = Column(ForeignKey("warehouses.id"), nullable=False)
    to_warehouse_id = Column(ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(ForeignKey("products.id"), nullable=False)
    variant_id = Column(ForeignKey("product_variants.id"))
    quantity = Column(Integer, nullable=False)
    dispatched_qty = Column(Integer, default=0)
    received_qty = Column(Integer, default=0)
    status = Column(String(20), default="requested")  # requested / dispatched / received / cancelled
    note = Column(String(255))
    created_by = Column(Integer)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)


class ThresholdHistory(Base):
    __tablename__ = "threshold_history"
    id = Column(Integer, primary_key=True)
    inventory_id = Column(ForeignKey("inventory.id", ondelete="CASCADE"))
    old_value = Column(Integer)
    new_value = Column(Integer)
    changed_by = Column(Integer)
    changed_at = Column(DateTime, default=now)


class RestockAlert(Base):
    __tablename__ = "restock_alerts"
    id = Column(Integer, primary_key=True)
    inventory_id = Column(ForeignKey("inventory.id", ondelete="CASCADE"), index=True)
    available_qty = Column(Integer)
    threshold = Column(Integer)
    status = Column(String(20), default="open")  # open / resolved
    created_at = Column(DateTime, default=now)
    resolved_at = Column(DateTime)