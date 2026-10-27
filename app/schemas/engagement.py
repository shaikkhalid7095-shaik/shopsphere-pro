from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORM


class ReviewIn(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = Field(None, max_length=150)
    comment: Optional[str] = Field(None, max_length=3000)


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewOut(ORM):
    id: int
    product_id: int
    user_id: int
    rating: int
    title: Optional[str]
    comment: Optional[str]
    status: str
    created_at: datetime


class ModerateIn(BaseModel):
    status: Literal["published", "hidden", "removed"]


class RatingSummary(BaseModel):
    product_id: int
    average: Optional[float]
    count: int
    breakdown: Dict[int, int]


class QuestionIn(BaseModel):
    product_id: int
    text: str = Field(min_length=5, max_length=1000)


class AnswerIn(BaseModel):
    text: str = Field(min_length=2, max_length=2000)


class AnswerOut(ORM):
    id: int
    user_id: int
    text: str
    status: str
    created_at: datetime


class QuestionOut(ORM):
    id: int
    product_id: int
    user_id: int
    text: str
    status: str
    created_at: datetime
    answers: List[AnswerOut] = []


class QAModerateIn(BaseModel):
    hide: bool


class TicketIn(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=3)
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    priority: Literal["low", "medium", "high", "urgent"] = "medium"


class TicketMessageIn(BaseModel):
    message: str = Field(min_length=1)
    is_internal: bool = False


class TicketMessageOut(ORM):
    id: int
    sender_id: int
    message: str
    is_internal: bool
    created_at: datetime


class TicketOut(ORM):
    id: int
    ticket_no: str
    user_id: int
    order_id: Optional[int]
    product_id: Optional[int]
    subject: str
    status: str
    priority: str
    assigned_to: Optional[int]
    resolution: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]


class TicketDetail(TicketOut):
    messages: List[TicketMessageOut] = []


class TicketAssignIn(BaseModel):
    agent_id: int


class TicketUpdateIn(BaseModel):
    status: Optional[Literal["open", "in_progress", "resolved", "closed"]] = None
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    resolution: Optional[str] = None


class NotificationOut(ORM):
    id: int
    title: Optional[str]
    message: Optional[str]
    kind: str
    is_read: bool
    created_at: datetime


class ProviderIn(BaseModel):
    channel: Literal["email", "sms"]
    name: Literal["console", "smtp", "fail"]
    config: Optional[dict] = None
    is_active: bool = True


class ProviderOut(ORM):
    id: int
    channel: str
    name: str
    is_active: bool


class OutboundOut(ORM):
    id: int
    channel: str
    recipient: str
    subject: Optional[str]
    template: Optional[str]
    status: str
    attempts: int
    max_attempts: int
    last_error: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]


class SendTestIn(BaseModel):
    channel: Literal["email", "sms"]
    recipient: str
    subject: Optional[str] = "Test message"
    body: str = "Hello from ShopSphere Pro"