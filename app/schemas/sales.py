from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import ORM


# ---------- cart ----------
class CartAddIn(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(1, gt=0, le=50)


class CartQtyIn(BaseModel):
    quantity: int = Field(gt=0, le=50)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int]
    name: str
    sku: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    available: int
    in_stock: bool


class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    item_count: int
    subtotal: Decimal
    coupon_code: Optional[str] = None


class SummaryIn(BaseModel):
    coupon_code: Optional[str] = None
    shipping_method_id: Optional[int] = None
    shipping_address_id: Optional[int] = None


class SummaryLine(BaseModel):
    product_id: int
    variant_id: Optional[int]
    name: str
    quantity: int
    unit_price: Decimal
    discount: Decimal
    tax: Decimal
    line_total: Decimal
    promotion: Optional[str] = None


class SummaryOut(BaseModel):
    lines: List[SummaryLine]
    subtotal: Decimal
    promotion_discount: Decimal
    coupon_discount: Decimal
    discount_total: Decimal
    tax_total: Decimal
    tax_breakdown: Dict[str, str]
    shipping_total: Decimal
    shipping_method: Optional[str]
    grand_total: Decimal
    item_count: int


class WishlistIn(BaseModel):
    product_id: int


class WishlistOut(BaseModel):
    id: int
    product_id: int
    name: str
    price: Decimal
    available: int
    is_active: bool
    added_at: datetime


# ---------- coupons ----------
class CouponIn(BaseModel):
    code: str = Field(min_length=3, max_length=40)
    description: Optional[str] = None
    discount_type: Literal["percent", "fixed"]
    value: Decimal = Field(gt=0)
    max_discount: Optional[Decimal] = Field(None, gt=0)
    min_purchase: Decimal = Field(0, ge=0)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, gt=0)
    is_active: bool = True

    @field_validator("code")
    @classmethod
    def upper(cls, v):
        return v.strip().upper()

    @model_validator(mode="after")
    def check(self):
        if self.discount_type == "percent" and self.value > 100:
            raise ValueError("Percent discount can't be over 100")
        if self.valid_from and self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be after valid_from")
        return self


class CouponOut(ORM):
    id: int
    code: str
    description: Optional[str]
    discount_type: str
    value: Decimal
    max_discount: Optional[Decimal]
    min_purchase: Optional[Decimal]
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    usage_limit: Optional[int]
    used_count: int
    is_active: bool


class ActiveIn(BaseModel):
    is_active: bool


# ---------- promotions ----------
class PromotionIn(BaseModel):
    name: str = Field(min_length=2)
    scope: Literal["product", "category"]
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    discount_type: Literal["percent", "fixed"]
    value: Decimal = Field(gt=0)
    min_quantity: int = Field(1, ge=1)
    start_at: datetime
    end_at: datetime
    is_active: bool = True

    @model_validator(mode="after")
    def check(self):
        if self.scope == "product" and not self.product_id:
            raise ValueError("product_id needed for product promotions")
        if self.scope == "category" and not self.category_id:
            raise ValueError("category_id needed for category promotions")
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        if self.discount_type == "percent" and self.value > 90:
            raise ValueError("Promotion percent can't be over 90")
        return self


class PromotionOut(ORM):
    id: int
    name: str
    scope: str
    product_id: Optional[int]
    category_id: Optional[int]
    discount_type: str
    value: Decimal
    min_quantity: int
    start_at: datetime
    end_at: datetime
    is_active: bool


class HistoryOut(ORM):
    id: int
    entity: str
    entity_id: int
    action: str
    data: Optional[dict]
    changed_by: Optional[int]
    changed_at: datetime


# ---------- tax ----------
class TaxIn(BaseModel):
    name: str
    rate: Decimal = Field(ge=0, le=100)
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    is_active: bool = True


class TaxOut(ORM):
    id: int
    name: str
    rate: Decimal
    product_id: Optional[int]
    category_id: Optional[int]
    is_active: bool


# ---------- shipping ----------
class ShippingIn(BaseModel):
    name: str
    code: str = Field(min_length=2, max_length=30)
    base_charge: Decimal = Field(0, ge=0)
    per_item_charge: Decimal = Field(0, ge=0)
    free_above: Optional[Decimal] = Field(None, ge=0)
    min_days: int = Field(3, ge=0)
    max_days: int = Field(7, ge=0)
    allowed_countries: Optional[str] = None
    max_items: Optional[int] = Field(None, gt=0)
    is_active: bool = True

    @model_validator(mode="after")
    def days(self):
        if self.max_days < self.min_days:
            raise ValueError("max_days must be >= min_days")
        return self


class ShippingOut(ORM):
    id: int
    name: str
    code: str
    base_charge: Decimal
    per_item_charge: Decimal
    free_above: Optional[Decimal]
    min_days: int
    max_days: int
    allowed_countries: Optional[str]
    max_items: Optional[int]
    is_active: bool


class ShippingQuoteIn(BaseModel):
    subtotal: Decimal = Field(ge=0)
    item_count: int = Field(gt=0)
    country: Optional[str] = None