from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORM


class CheckoutIn(BaseModel):
    shipping_address_id: int
    billing_address_id: Optional[int] = None  # same as shipping if empty
    shipping_method_id: int
    payment_method: Literal["card", "cod"] = "card"
    coupon_code: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)


class OrderItemOut(ORM):
    id: int
    product_id: int
    variant_id: Optional[int]
    sku: Optional[str]
    product_name: Optional[str]
    product_description: Optional[str]
    variant_label: Optional[str]
    unit_price: Decimal
    quantity: int
    discount: Decimal
    tax: Decimal
    line_total: Decimal
    fulfillment_status: str


class OrderOut(ORM):
    id: int
    order_number: str
    user_id: int
    status: str
    payment_method: str
    payment_status: str
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    shipping_total: Decimal
    grand_total: Decimal
    coupon_code: Optional[str]
    created_at: datetime


class StatusHistoryOut(ORM):
    id: int
    from_status: Optional[str]
    to_status: str
    changed_by: Optional[int]
    note: Optional[str]
    created_at: datetime


class OrderDetail(OrderOut):
    shipping_address_text: Optional[str]
    billing_address_text: Optional[str]
    shipping_method_id: Optional[int]
    tax_breakdown: Optional[dict]
    notes: Optional[str]
    items: List[OrderItemOut]
    history: List[StatusHistoryOut] = []


class StatusChangeIn(BaseModel):
    status: Literal["confirmed", "processing", "shipped", "delivered"]
    note: Optional[str] = None


class ItemStatusIn(BaseModel):
    fulfillment_status: Literal["pending", "packed", "shipped", "delivered"]


class CancelIn(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class CancellationOut(ORM):
    id: int
    order_id: int
    requested_by: Optional[int]
    reason: Optional[str]
    outcome: Optional[str]
    refund_id: Optional[int]
    created_at: datetime