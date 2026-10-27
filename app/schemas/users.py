import re
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.common import ORM

PHONE_RE = re.compile(r"^\+?[0-9]{10,13}$")


def check_phone(v):
    if v is None:
        return v
    v = v.replace(" ", "").replace("-", "")
    if not PHONE_RE.match(v):
        raise ValueError("Phone must be 10-13 digits, optional + at start")
    return v


def check_password(v):
    if len(v) < 8 or not re.search(r"[A-Za-z]", v) or not re.search(r"[0-9]", v):
        raise ValueError("Password needs 8+ characters with letters and numbers")
    return v


# ---------- auth ----------
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshIn(BaseModel):
    refresh_token: str


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str
    _v = field_validator("new_password")(check_password)


# ---------- registration ----------
class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str
    password: str

    _p = field_validator("phone")(check_phone)
    _pw = field_validator("password")(check_password)


class RegisterOut(BaseModel):
    id: int
    email: str
    registration_status: str
    message: str
    verify_token: Optional[str] = None  # only returned when DEBUG=true so you can test easily


# ---------- users / roles ----------
class PermissionOut(ORM):
    id: int
    code: str
    description: Optional[str] = None


class RoleOut(ORM):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionOut] = []


class UserOut(ORM):
    id: int
    email: str
    phone: Optional[str] = None
    full_name: str
    role_name: Optional[str] = None
    status: str
    registration_status: Optional[str] = None
    is_email_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: str

    _p = field_validator("phone")(check_phone)
    _pw = field_validator("password")(check_password)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

    _p = field_validator("phone")(check_phone)


class StatusIn(BaseModel):
    status: Literal["active", "inactive", "suspended"]


class RoleAssignIn(BaseModel):
    role: str


class RolePermissionsIn(BaseModel):
    permissions: List[str]


class ActivityOut(ORM):
    id: int
    action: str
    detail: Optional[str] = None
    created_at: datetime


# ---------- profile ----------
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    _p = field_validator("phone")(check_phone)


class ProfileHistoryOut(ORM):
    id: int
    field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: datetime


class DeactivationIn(BaseModel):
    reason: str = Field(min_length=3)


class DeactivationOut(ORM):
    id: int
    user_id: int
    reason: Optional[str]
    status: str
    created_at: datetime


class DeactivationReview(BaseModel):
    approve: bool


# ---------- address ----------
class AddressIn(BaseModel):
    label: Optional[str] = None
    address_type: Literal["shipping", "billing"] = "shipping"
    full_name: str = Field(min_length=2)
    phone: str
    line1: str = Field(min_length=3)
    line2: Optional[str] = None
    city: str = Field(min_length=2)
    state: str = Field(min_length=2)
    postal_code: str = Field(pattern=r"^[0-9A-Za-z \-]{4,10}$")
    country: str = "India"
    is_default: bool = False

    _p = field_validator("phone")(check_phone)


class AddressOut(ORM):
    id: int
    label: Optional[str]
    address_type: str
    full_name: str
    phone: str
    line1: str
    line2: Optional[str]
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool