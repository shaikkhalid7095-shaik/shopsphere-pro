from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORM

SHIPMENT_STATUSES = Literal["in_transit", "out_for_delivery", "delivered", "exception", "returned"]


class ProviderIn(BaseModel):
    name: str
    code: str = Field(min_length=2, max_length=30)
    tracking_url: Optional[str] = None
    is_active: bool = True


class ProviderOut(ORM):
    id: int
    name: str
    code: str
    tracking_url: Optional[str]
    is_active: bool


class ShipmentIn(BaseModel):
    order_id: int
    provider_id: int
    tracking_number: Optional[str] = None
    weight_kg: Optional[str] = None


class TrackingEventOut(ORM):
    id: int
    status: str
    location: Optional[str]
    description: Optional[str]
    is_exception: bool
    source: str
    event_time: datetime


class ShipmentOut(ORM):
    id: int
    shipment_ref: str
    order_id: int
    provider_id: Optional[int]
    tracking_number: Optional[str]
    status: str
    dispatched_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime


class ShipmentDetail(ShipmentOut):
    events: List[TrackingEventOut] = []
    tracking_link: Optional[str] = None


class TrackingIn(BaseModel):
    status: SHIPMENT_STATUSES
    location: Optional[str] = None
    description: Optional[str] = None


class ProviderUpdateIn(TrackingIn):
    tracking_number: str


class AssignIn(BaseModel):
    assigned_to: Optional[int] = None
    provider_id: Optional[int] = None

    @model_validator(mode="after")
    def one(self):
        if not self.assigned_to and not self.provider_id:
            raise ValueError("Give assigned_to (user id) or provider_id")
        return self


class AttemptIn(BaseModel):
    result: Literal["delivered", "failed"]
    reason: Optional[str] = None
    receiver_name: Optional[str] = None
    proof_note: Optional[str] = None

    @model_validator(mode="after")
    def need(self):
        if self.result == "failed" and not self.reason:
            raise ValueError("reason is required for a failed attempt")
        if self.result == "delivered" and not self.receiver_name:
            raise ValueError("receiver_name is required to confirm delivery")
        return self


class AttemptOut(ORM):
    id: int
    attempt_no: int
    result: str
    reason: Optional[str]
    attempted_by: Optional[int]
    attempted_at: datetime


class AssignmentOut(ORM):
    id: int
    shipment_id: int
    assigned_to: Optional[int]
    provider_id: Optional[int]
    status: str
    attempts: int
    receiver_name: Optional[str]
    proof_note: Optional[str]
    delivered_at: Optional[datetime]
    created_at: datetime


class AssignmentDetail(AssignmentOut):
    attempt_history: List[AttemptOut] = []


# ---------- returns / exchanges ----------
class ReturnItemIn(BaseModel):
    order_item_id: int
    quantity: int = Field(gt=0)
    reason: Optional[str] = None


class ReturnIn(BaseModel):
    order_id: int
    reason: str = Field(min_length=3)
    items: List[ReturnItemIn] = Field(min_length=1)


class ReturnItemOut(ORM):
    id: int
    order_item_id: int
    quantity: int
    reason: Optional[str]


class ReturnOut(ORM):
    id: int
    return_no: str
    order_id: int
    user_id: int
    reason: Optional[str]
    status: str
    admin_note: Optional[str]
    refund_id: Optional[int]
    created_at: datetime
    items: List[ReturnItemOut]


class ReviewDecisionIn(BaseModel):
    approve: bool
    note: Optional[str] = None


class ReceiveIn(BaseModel):
    warehouse_id: int
    restock: bool = True  # false if the item is damaged


class ExchangeIn(BaseModel):
    order_item_id: int
    replacement_variant_id: int
    quantity: int = Field(1, gt=0)
    reason: str = Field(min_length=3)


class ExchangeOut(ORM):
    id: int
    exchange_no: str
    order_id: int
    order_item_id: int
    user_id: int
    replacement_variant_id: Optional[int]
    quantity: int
    reason: Optional[str]
    status: str
    created_at: datetime


class ExchangeEventOut(ORM):
    id: int
    status: str
    note: Optional[str]
    changed_by: Optional[int]
    created_at: datetime


class ExchangeDetail(ExchangeOut):
    events: List[ExchangeEventOut] = []