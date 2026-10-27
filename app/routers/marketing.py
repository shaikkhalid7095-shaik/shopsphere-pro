# Module 21 promotions, 22 tax, 23 shipping configuration
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Category, ConfigHistory, Product, Promotion, ShippingMethod, TaxRate, User
from app.roles import ADMIN, FINANCE_MANAGER, PRODUCT_MANAGER
from app.schemas.common import Page
from app.schemas.sales import (ActiveIn, HistoryOut, PromotionIn, PromotionOut, ShippingIn, ShippingOut,
                               ShippingQuoteIn, TaxIn, TaxOut)
from app.services.audit import log_action, row_to_dict, save_history
from app.services.pricing import shipping_charge
from app.utils import get_or_404, now, paginate

router = APIRouter(tags=["21. Promotions, 22. Tax, 23. Shipping"])
marketing_staff = require_roles(ADMIN, PRODUCT_MANAGER)
tax_staff = require_roles(ADMIN, FINANCE_MANAGER)


# ---------------- promotions ----------------
def _check_promo_refs(db, data):
    if data.product_id:
        get_or_404(db, Product, data.product_id, "Product")
    if data.category_id:
        get_or_404(db, Category, data.category_id, "Category")


@router.get("/promotions", response_model=Page[PromotionOut])
def list_promotions(current_only: bool = False, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    q = db.query(Promotion)
    if current_only:
        t = now()
        q = q.filter(Promotion.is_active.is_(True), Promotion.start_at <= t, Promotion.end_at >= t)
    return paginate(q.order_by(Promotion.id.desc()), page, size)


@router.post("/promotions", response_model=PromotionOut, status_code=201)
def create_promotion(data: PromotionIn, db: Session = Depends(get_db), me: User = Depends(marketing_staff)):
    _check_promo_refs(db, data)
    p = Promotion(**data.model_dump())
    if data.scope == "product":
        p.category_id = None
    else:
        p.product_id = None
    db.add(p)
    db.flush()
    save_history(db, "promotion", p.id, "created", data.model_dump(), me.id)
    db.commit()
    return p


@router.put("/promotions/{promo_id}", response_model=PromotionOut)
def update_promotion(promo_id: int, data: PromotionIn, db: Session = Depends(get_db),
                     me: User = Depends(marketing_staff)):
    p = get_or_404(db, Promotion, promo_id, "Promotion")
    _check_promo_refs(db, data)
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    save_history(db, "promotion", p.id, "updated", data.model_dump(), me.id)
    db.commit()
    return p


@router.put("/promotions/{promo_id}/status", response_model=PromotionOut)
def promotion_status(promo_id: int, data: ActiveIn, db: Session = Depends(get_db),
                     me: User = Depends(marketing_staff)):
    p = get_or_404(db, Promotion, promo_id, "Promotion")
    p.is_active = data.is_active
    save_history(db, "promotion", p.id, "activated" if data.is_active else "deactivated", {}, me.id)
    db.commit()
    return p


@router.get("/promotions/{promo_id}/history", response_model=list[HistoryOut])
def promotion_history(promo_id: int, db: Session = Depends(get_db), _=Depends(marketing_staff)):
    return db.query(ConfigHistory).filter_by(entity="promotion", entity_id=promo_id).order_by(ConfigHistory.id).all()


# ---------------- tax ----------------
@router.get("/tax-rates", response_model=list[TaxOut])
def list_tax(db: Session = Depends(get_db), _=Depends(require_roles(ADMIN, FINANCE_MANAGER, PRODUCT_MANAGER))):
    return db.query(TaxRate).order_by(TaxRate.id).all()


@router.post("/tax-rates", response_model=TaxOut, status_code=201)
def create_tax(data: TaxIn, db: Session = Depends(get_db), me: User = Depends(tax_staff)):
    if data.product_id and data.category_id:
        raise HTTPException(400, "Tax rule can be for a product OR a category, not both")
    if data.product_id:
        get_or_404(db, Product, data.product_id, "Product")
    if data.category_id:
        get_or_404(db, Category, data.category_id, "Category")
    clash = db.query(TaxRate).filter_by(product_id=data.product_id, category_id=data.category_id,
                                        is_active=True).first()
    if clash and data.is_active:
        raise HTTPException(409, f"An active tax rule already exists for this target (#{clash.id})")
    t = TaxRate(**data.model_dump())
    db.add(t)
    db.flush()
    save_history(db, "tax_rate", t.id, "created", data.model_dump(), me.id)
    db.commit()
    return t


@router.put("/tax-rates/{tax_id}", response_model=TaxOut)
def update_tax(tax_id: int, data: TaxIn, db: Session = Depends(get_db), me: User = Depends(tax_staff)):
    t = get_or_404(db, TaxRate, tax_id, "Tax rate")
    old = row_to_dict(t)
    for k, v in data.model_dump().items():
        setattr(t, k, v)
    save_history(db, "tax_rate", t.id, "updated", {"old": old, "new": data.model_dump()}, me.id)
    log_action(db, me.id, "tax.update", "tax_rate", t.id, old, data.model_dump())
    db.commit()
    return t


@router.get("/tax-rates/{tax_id}/history", response_model=list[HistoryOut])
def tax_history(tax_id: int, db: Session = Depends(get_db), _=Depends(tax_staff)):
    return db.query(ConfigHistory).filter_by(entity="tax_rate", entity_id=tax_id).order_by(ConfigHistory.id).all()


# ---------------- shipping ----------------
@router.get("/shipping-methods", response_model=list[ShippingOut])
def list_shipping(include_inactive: bool = False, db: Session = Depends(get_db)):
    q = db.query(ShippingMethod)
    if not include_inactive:
        q = q.filter(ShippingMethod.is_active.is_(True))
    return q.order_by(ShippingMethod.base_charge).all()


@router.post("/shipping-methods", response_model=ShippingOut, status_code=201)
def create_shipping(data: ShippingIn, db: Session = Depends(get_db), me: User = Depends(require_roles(ADMIN))):
    if db.query(ShippingMethod).filter_by(code=data.code).first():
        raise HTTPException(409, "Shipping code exists")
    m = ShippingMethod(**data.model_dump())
    db.add(m)
    db.commit()
    return m


@router.put("/shipping-methods/{method_id}", response_model=ShippingOut)
def update_shipping(method_id: int, data: ShippingIn, db: Session = Depends(get_db),
                    me: User = Depends(require_roles(ADMIN))):
    m = get_or_404(db, ShippingMethod, method_id, "Shipping method")
    for k, v in data.model_dump().items():
        setattr(m, k, v)
    db.commit()
    return m


@router.put("/shipping-methods/{method_id}/status", response_model=ShippingOut)
def shipping_status(method_id: int, data: ActiveIn, db: Session = Depends(get_db),
                    me: User = Depends(require_roles(ADMIN))):
    m = get_or_404(db, ShippingMethod, method_id, "Shipping method")
    m.is_active = data.is_active
    db.commit()
    return m


@router.post("/shipping-methods/{method_id}/quote")
def shipping_quote(method_id: int, data: ShippingQuoteIn, db: Session = Depends(get_db)):
    m = get_or_404(db, ShippingMethod, method_id, "Shipping method")
    charge = shipping_charge(m, data.subtotal, data.item_count, data.country)
    return {"method": m.name, "charge": charge, "delivery_days": f"{m.min_days}-{m.max_days}"}