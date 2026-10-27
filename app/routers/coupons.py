# Module 20: coupon management
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import Coupon, User
from app.roles import ADMIN, PRODUCT_MANAGER
from app.schemas.common import Page
from app.schemas.sales import ActiveIn, CouponIn, CouponOut
from app.services.audit import log_action, row_to_dict
from app.services.pricing import coupon_discount, validate_coupon
from app.utils import get_or_404, money, paginate

router = APIRouter(tags=["20. Coupons"])
marketing_staff = require_roles(ADMIN, PRODUCT_MANAGER)


# ---------------- coupons ----------------
@router.get("/coupons", response_model=Page[CouponOut])
def list_coupons(active: Optional[bool] = None, page: int = 1, size: int = 20, db: Session = Depends(get_db),
                 _=Depends(marketing_staff)):
    q = db.query(Coupon)
    if active is not None:
        q = q.filter(Coupon.is_active.is_(active))
    return paginate(q.order_by(Coupon.id.desc()), page, size)


@router.post("/coupons", response_model=CouponOut, status_code=201)
def create_coupon(data: CouponIn, db: Session = Depends(get_db), me: User = Depends(marketing_staff)):
    if db.query(Coupon).filter_by(code=data.code).first():
        raise HTTPException(409, "Coupon code exists")
    c = Coupon(**data.model_dump())
    db.add(c)
    db.flush()
    log_action(db, me.id, "coupon.create", "coupon", c.id, None, data.model_dump())
    db.commit()
    return c


@router.put("/coupons/{coupon_id}", response_model=CouponOut)
def update_coupon(coupon_id: int, data: CouponIn, db: Session = Depends(get_db), me: User = Depends(marketing_staff)):
    c = get_or_404(db, Coupon, coupon_id, "Coupon")
    if db.query(Coupon).filter(Coupon.code == data.code, Coupon.id != c.id).first():
        raise HTTPException(409, "Coupon code exists")
    if data.usage_limit is not None and data.usage_limit < c.used_count:
        raise HTTPException(400, f"Coupon already used {c.used_count} times")
    old = row_to_dict(c)
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    log_action(db, me.id, "coupon.update", "coupon", c.id, old, data.model_dump())
    db.commit()
    return c


@router.put("/coupons/{coupon_id}/status", response_model=CouponOut)
def coupon_status(coupon_id: int, data: ActiveIn, db: Session = Depends(get_db), me: User = Depends(marketing_staff)):
    c = get_or_404(db, Coupon, coupon_id, "Coupon")
    c.is_active = data.is_active
    db.commit()
    return c


@router.get("/coupons/validate/{code}")
def check_coupon(code: str, subtotal: float, db: Session = Depends(get_db), _=Depends(get_current_user)):
    c = validate_coupon(db, code, money(subtotal))
    return {"code": c.code, "valid": True, "discount": coupon_discount(c, money(subtotal))}