from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import now


class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    coupon_code = Column(String(40))
    updated_at = Column(DateTime, default=now, onupdate=now)

    items = relationship("CartItem", cascade="all, delete-orphan", lazy="selectin")


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    cart_id = Column(ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(ForeignKey("product_variants.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=now)

    product = relationship("Product", lazy="joined")
    variant = relationship("ProductVariant", lazy="joined")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_wishlist"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime, default=now)

    product = relationship("Product", lazy="joined")


class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False)
    description = Column(String(255))
    discount_type = Column(String(10), nullable=False)  # percent / fixed
    value = Column(Numeric(10, 2), nullable=False)
    max_discount = Column(Numeric(10, 2))
    min_purchase = Column(Numeric(10, 2), default=0)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    usage_limit = Column(Integer)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class Promotion(Base):
    __tablename__ = "promotions"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    scope = Column(String(20), nullable=False)  # product / category
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"))
    category_id = Column(ForeignKey("categories.id", ondelete="CASCADE"))
    discount_type = Column(String(10), nullable=False)  # percent / fixed (per unit)
    value = Column(Numeric(10, 2), nullable=False)
    min_quantity = Column(Integer, default=1)  # eligibility rule
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class TaxRate(Base):
    __tablename__ = "tax_rates"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)  # percent e.g. 18.00
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"))
    category_id = Column(ForeignKey("categories.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class ShippingMethod(Base):
    __tablename__ = "shipping_methods"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    base_charge = Column(Numeric(10, 2), default=0)
    per_item_charge = Column(Numeric(10, 2), default=0)
    free_above = Column(Numeric(10, 2))  # order subtotal for free shipping
    min_days = Column(Integer, default=3)
    max_days = Column(Integer, default=7)
    allowed_countries = Column(String(255))  # comma separated, empty = all
    max_items = Column(Integer)  # eligibility rule
    is_active = Column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_number = Column(String(40), unique=True, nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    # pending / confirmed / processing / shipped / delivered / cancelled
    status = Column(String(20), default="pending", nullable=False, index=True)
    payment_method = Column(String(10), nullable=False)  # card / cod
    # unpaid / paid / failed / refunded / partially_refunded / cod_pending
    payment_status = Column(String(20), default="unpaid")
    shipping_address_id = Column(ForeignKey("addresses.id"))
    billing_address_id = Column(ForeignKey("addresses.id"))
    shipping_address_text = Column(Text)
    billing_address_text = Column(Text)
    shipping_method_id = Column(ForeignKey("shipping_methods.id"))
    coupon_code = Column(String(40))
    subtotal = Column(Numeric(12, 2), default=0)
    discount_total = Column(Numeric(12, 2), default=0)
    tax_total = Column(Numeric(12, 2), default=0)
    shipping_total = Column(Numeric(12, 2), default=0)
    grand_total = Column(Numeric(12, 2), default=0)
    tax_breakdown = Column(JSON)
    idempotency_key = Column(String(80), unique=True)
    notes = Column(String(500))
    created_at = Column(DateTime, default=now, index=True)
    updated_at = Column(DateTime, default=now, onupdate=now)

    items = relationship("OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(ForeignKey("products.id"), nullable=False)
    variant_id = Column(ForeignKey("product_variants.id"))
    inventory_id = Column(ForeignKey("inventory.id"))  # stock row we reserved from
    # snapshots so later product edits don't change old orders
    sku = Column(String(60))
    product_name = Column(String(200))
    product_description = Column(Text)
    variant_label = Column(String(80))
    unit_price = Column(Numeric(12, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    discount = Column(Numeric(12, 2), default=0)
    tax = Column(Numeric(12, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    # pending / packed / shipped / delivered / cancelled / returned
    fulfillment_status = Column(String(20), default="pending")

    order = relationship("Order", back_populates="items")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    from_status = Column(String(20))
    to_status = Column(String(20))
    changed_by = Column(Integer)
    note = Column(String(255))
    created_at = Column(DateTime, default=now)


class OrderCancellation(Base):
    __tablename__ = "order_cancellations"
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey("orders.id", ondelete="CASCADE"), unique=True)
    requested_by = Column(Integer)
    reason = Column(String(500))
    outcome = Column(String(255))
    refund_id = Column(Integer)
    created_at = Column(DateTime, default=now)