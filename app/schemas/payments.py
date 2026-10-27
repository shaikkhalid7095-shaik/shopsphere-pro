from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORM


class PaymentOut(ORM):
    id: int
    order_id: int
    user_id: int
    amount: Decimal
    currency: str
    method: str
    gateway: Optional[str]
    gateway_ref: Optional[str]
    status: str
    failure_reason: Optional[str]
    created_at: datetime


class IntentOut(PaymentOut):
    client_secret: Optional[str]
    is_existing: bool = False


class PaymentEventOut(ORM):
    id: int
    event_type: Optional[str]
    status: Optional[str]
    gateway_event_id: Optional[str]
    created_at: datetime


class PaymentDetail(PaymentOut):
    events: List[PaymentEventOut] = []


class RefundIn(BaseModel):
    order_id: int
    amount: Decimal = Field(gt=0)
    reason: str = Field(min_length=3)
    process_now: bool = True


class RefundOut(ORM):
    id: int
    refund_no: Optional[str]
    order_id: int
    payment_id: Optional[int]
    amount: Decimal
    reason: Optional[str]
    status: str
    gateway_ref: Optional[str]
    requested_by: Optional[int]
    processed_by: Optional[int]
    created_at: datetime
    processed_at: Optional[datetime]


class CodSettingIn(BaseModel):
    is_enabled: bool = True
    max_order_amount: Decimal = Field(gt=0)
    allowed_countries: str = "India"
    blocked_postal_codes: str = ""


class CodSettingOut(ORM):
    is_enabled: bool
    max_order_amount: Decimal
    allowed_countries: Optional[str]
    blocked_postal_codes: Optional[str]


class CodCollectIn(BaseModel):
    amount: Decimal = Field(ge=0)
    note: Optional[str] = None


class CodReconcileIn(BaseModel):
    note: Optional[str] = None


class CodOut(ORM):
    id: int
    order_id: int
    expected_amount: Decimal
    collected_amount: Optional[Decimal]
    status: str
    collected_by: Optional[int]
    collected_at: Optional[datetime]
    reconciled_by: Optional[int]
    reconciled_at: Optional[datetime]
    note: Optional[str]