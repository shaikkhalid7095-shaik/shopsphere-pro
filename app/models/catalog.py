from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import now


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(150), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(60), unique=True, nullable=False)
    description = Column(Text)
    category_id = Column(ForeignKey("categories.id"), nullable=False)
    brand_id = Column(ForeignKey("brands.id"), nullable=True)
    seller_id = Column(ForeignKey("suppliers.id"), nullable=True)
    base_price = Column(Numeric(12, 2), nullable=False)
    sale_price = Column(Numeric(12, 2))
    sale_start = Column(DateTime)
    sale_end = Column(DateTime)
    cod_allowed = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    category = relationship("Category", lazy="joined")
    brand = relationship("Brand", lazy="joined")
    variants = relationship("ProductVariant", back_populates="product", lazy="selectin")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku = Column(String(60), unique=True, nullable=False)
    size = Column(String(30))
    color = Column(String(30))
    price = Column(Numeric(12, 2))  # null -> use product price
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

    product = relationship("Product", back_populates="variants")


class ProductFile(Base):
    __tablename__ = "product_files"
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(ForeignKey("product_variants.id", ondelete="SET NULL"))
    file_kind = Column(String(20), default="image")  # image / document
    original_name = Column(String(255))
    stored_name = Column(String(255), nullable=False)
    content_type = Column(String(100))
    size_bytes = Column(Integer)
    uploaded_by = Column(Integer)
    created_at = Column(DateTime, default=now)


class Attribute(Base):
    __tablename__ = "attributes"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    data_type = Column(String(20), default="text")  # text / number / choice
    allowed_values = Column(String(500))  # comma separated for choice
    category_id = Column(ForeignKey("categories.id"), nullable=True)  # null = all categories


class ProductAttributeValue(Base):
    __tablename__ = "product_attribute_values"
    __table_args__ = (UniqueConstraint("product_id", "attribute_id", name="uq_product_attribute"),)
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    attribute_id = Column(ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(255), nullable=False)

    attribute = relationship("Attribute", lazy="joined")


class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    variant_id = Column(Integer)
    old_base = Column(Numeric(12, 2))
    new_base = Column(Numeric(12, 2))
    old_sale = Column(Numeric(12, 2))
    new_sale = Column(Numeric(12, 2))
    changed_by = Column(Integer)
    changed_at = Column(DateTime, default=now)