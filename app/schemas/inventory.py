from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORM


class WarehouseIn(BaseModel):
    name: str = Field(min_length=2)
    code: str = Field(min_length=2, max_length=20)
    city: Optional[str] = None
    capacity: int = Field(10000, gt=0)
    is_active: bool = True


class WarehouseOut(ORM):
    id: int
    name: str
    code: str
    city: Optional[str]
    capacity: int
    is_active: bool


class StockOut(ORM):
    id: int
    product_id: int
    variant_id: Optional[int]
    warehouse_id: int
    quantity: int
    reserved: int
    available: int
    min_threshold: int


class StockAdjustIn(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    warehouse_id: int
    quantity: int = Field(gt=0)
    action: Literal["add", "remove"]
    note: Optional[str] = None


class MovementOut(ORM):
    id: int
    inventory_id: int
    change: int
    movement_type: str
    reference: Optional[str]
    note: Optional[str]
    created_by: Optional[int]
    created_at: datetime


class TransferIn(BaseModel):
    from_warehouse_id: int
    to_warehouse_id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(gt=0)
    note: Optional[str] = None

    @model_validator(mode="after")
    def diff(self):
        if self.from_warehouse_id == self.to_warehouse_id:
            raise ValueError("Source and destination warehouse must be different")
        return self


class TransferQtyIn(BaseModel):
    quantity: int = Field(gt=0)


class TransferOut(ORM):
    id: int
    transfer_no: str
    from_warehouse_id: int
    to_warehouse_id: int
    product_id: int
    variant_id: Optional[int]
    quantity: int
    dispatched_qty: int
    received_qty: int
    status: str
    note: Optional[str]
    created_at: datetime


class ThresholdIn(BaseModel):
    min_threshold: int = Field(ge=0)


class ThresholdHistoryOut(ORM):
    id: int
    inventory_id: int
    old_value: Optional[int]
    new_value: int
    changed_by: Optional[int]
    changed_at: datetime


class AlertOut(ORM):
    id: int
    inventory_id: int
    available_qty: int
    threshold: int
    status: str
    created_at: datetime