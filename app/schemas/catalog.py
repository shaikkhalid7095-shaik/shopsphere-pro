from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORM


class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryOut(ORM):
    id: int
    name: str
    slug: str
    description: Optional[str]
    parent_id: Optional[int]
    is_active: bool


class CategoryTree(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    children: List["CategoryTree"] = []


class BrandIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = None
    is_active: bool = True


class BrandOut(ORM):
    id: int
    name: str
    description: Optional[str]
    is_active: bool


class ActiveIn(BaseModel):
    is_active: bool


class VariantIn(BaseModel):
    sku: str = Field(min_length=2, max_length=60)
    size: Optional[str] = None
    color: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    is_active: bool = True


class VariantUpdate(BaseModel):
    size: Optional[str] = None
    color: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None


class VariantOut(ORM):
    id: int
    product_id: int
    sku: str
    size: Optional[str]
    color: Optional[str]
    price: Optional[Decimal]
    is_active: bool
    available: Optional[int] = None


class ProductIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    sku: str = Field(min_length=2, max_length=60)
    description: Optional[str] = None
    category_id: int
    brand_id: Optional[int] = None
    seller_id: Optional[int] = None
    base_price: Decimal = Field(gt=0)
    sale_price: Optional[Decimal] = Field(None, gt=0)
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None
    cod_allowed: bool = True

    @model_validator(mode="after")
    def check_sale(self):
        if self.sale_price is not None and self.sale_price >= self.base_price:
            raise ValueError("Sale price must be lower than base price")
        if self.sale_start and self.sale_end and self.sale_end <= self.sale_start:
            raise ValueError("Sale end must be after sale start")
        return self


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    seller_id: Optional[int] = None
    cod_allowed: Optional[bool] = None


class ProductOut(ORM):
    id: int
    name: str
    sku: str
    description: Optional[str]
    category_id: int
    brand_id: Optional[int]
    seller_id: Optional[int]
    base_price: Decimal
    sale_price: Optional[Decimal]
    sale_start: Optional[datetime]
    sale_end: Optional[datetime]
    cod_allowed: bool
    is_active: bool
    created_at: datetime


class AttrValueOut(BaseModel):
    attribute_id: int
    name: str
    value: str


class FileOut(ORM):
    id: int
    product_id: int
    variant_id: Optional[int]
    file_kind: str
    original_name: Optional[str]
    content_type: Optional[str]
    size_bytes: Optional[int]
    created_at: datetime


class ProductDetail(ProductOut):
    current_price: Decimal
    category_name: Optional[str] = None
    brand_name: Optional[str] = None
    available: int = 0
    variants: List[VariantOut] = []
    attributes: List[AttrValueOut] = []
    files: List[FileOut] = []
    rating_avg: Optional[float] = None
    rating_count: int = 0


class AttributeIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    data_type: Literal["text", "number", "choice"] = "text"
    allowed_values: Optional[List[str]] = None
    category_id: Optional[int] = None

    @model_validator(mode="after")
    def need_values(self):
        if self.data_type == "choice" and not self.allowed_values:
            raise ValueError("choice attributes need allowed_values")
        return self


class AttributeOut(ORM):
    id: int
    name: str
    data_type: str
    allowed_values: Optional[str]
    category_id: Optional[int]


class AssignAttributeIn(BaseModel):
    attribute_id: int
    value: str = Field(min_length=1, max_length=255)


class PriceIn(BaseModel):
    base_price: Optional[Decimal] = Field(None, gt=0)
    sale_price: Optional[Decimal] = Field(None, gt=0)
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None
    remove_sale: bool = False


class PriceHistoryOut(ORM):
    id: int
    product_id: int
    variant_id: Optional[int]
    old_base: Optional[Decimal]
    new_base: Optional[Decimal]
    old_sale: Optional[Decimal]
    new_sale: Optional[Decimal]
    changed_by: Optional[int]
    changed_at: datetime