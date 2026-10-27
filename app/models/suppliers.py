from sqlalchemy import (Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import now


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    kind = Column(String(20), default="supplier")  # supplier / seller
    contact_name = Column(String(150))
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    gst_number = Column(String(30))
    address = Column(Text)
    # pending / approved / rejected / suspended
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)


class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    __table_args__ = (UniqueConstraint("supplier_id", "product_id", name="uq_supplier_product"),)
    id = Column(Integer, primary_key=True)
    supplier_id = Column(ForeignKey("suppliers.id", ondelete="CASCADE"))
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"))
    cost_price = Column(Numeric(12, 2))


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    po_number = Column(String(40), unique=True)
    supplier_id = Column(ForeignKey("suppliers.id"), nullable=False)
    warehouse_id = Column(ForeignKey("warehouses.id"), nullable=False)
    # draft / sent / partially_received / received / cancelled
    status = Column(String(30), default="draft")
    expected_date = Column(Date)
    total_amount = Column(Numeric(12, 2), default=0)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=now)

    items = relationship("PurchaseOrderItem", lazy="selectin", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id = Column(Integer, primary_key=True)
    po_id = Column(ForeignKey("purchase_orders.id", ondelete="CASCADE"))
    product_id = Column(ForeignKey("products.id"), nullable=False)
    variant_id = Column(ForeignKey("product_variants.id"))
    quantity = Column(Integer, nullable=False)
    received_qty = Column(Integer, default=0)
    unit_cost = Column(Numeric(12, 2), nullable=False)


class SupplierInvoice(Base):
    __tablename__ = "supplier_invoices"
    __table_args__ = (UniqueConstraint("supplier_id", "invoice_number", name="uq_supplier_invoice"),)
    id = Column(Integer, primary_key=True)
    supplier_id = Column(ForeignKey("suppliers.id"), nullable=False)
    po_id = Column(ForeignKey("purchase_orders.id"), nullable=False)
    invoice_number = Column(String(60), nullable=False)
    invoice_date = Column(Date)
    amount = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0)
    # unpaid / partially_paid / paid / disputed
    status = Column(String(20), default="unpaid")
    created_at = Column(DateTime, default=now)