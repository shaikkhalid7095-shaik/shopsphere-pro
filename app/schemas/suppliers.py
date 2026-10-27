from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORM


class SupplierIn(BaseModel):
    name: str = Field(min_length=2)
    kind: Literal["supplier", "seller"] = "supplier"
    contact_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    gst_number: Optional[str] = Field(None, pattern=r"^[0-9A-Z]{15}$")
    address: Optional[str] = None


class SupplierOut(ORM):
    id: int
    name: str
    kind: str
    contact_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    gst_number: Optional[str]
    address: Optional[str]
    status: str
    created_at: datetime


class SupplierStatusIn(BaseModel):
    status: Literal["approved", "rejected", "suspended", "pending"]
    note: Optional[str] = None


class LinkProductIn(BaseModel):
    product_id: int
    cost_price: Optional[Decimal] = Field(None, gt=0)


class POItemIn(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(gt=0)
    unit_cost: Decimal = Field(gt=0)


class POIn(BaseModel):
    supplier_id: int
    warehouse_id: int
    expected_date: Optional[date] = None
    items: List[POItemIn] = Field(min_length=1)


class POItemOut(ORM):
    id: int
    product_id: int
    variant_id: Optional[int]
    quantity: int
    received_qty: int
    unit_cost: Decimal


class POOut(ORM):
    id: int
    po_number: str
    supplier_id: int
    warehouse_id: int
    status: str
    expected_date: Optional[date]
    total_amount: Decimal
    created_at: datetime
    items: List[POItemOut]


class ReceiveLine(BaseModel):
    po_item_id: int
    quantity: int = Field(gt=0)


class POReceiveIn(BaseModel):
    lines: List[ReceiveLine] = Field(min_length=1)


class InvoiceIn(BaseModel):
    po_id: int
    invoice_number: str = Field(min_length=1, max_length=60)
    invoice_date: date
    amount: Decimal = Field(gt=0)


class InvoicePayIn(BaseModel):
    amount: Decimal = Field(gt=0)


class InvoiceOut(ORM):
    id: int
    supplier_id: int
    po_id: int
    invoice_number: str
    invoice_date: Optional[date]
    amount: Decimal
    paid_amount: Decimal
    status: str
    created_at: datetime