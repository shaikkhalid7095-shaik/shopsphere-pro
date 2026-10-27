# Module 12: product pricing - base/sale price, validity period, history
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import PriceHistory, Product, User
from app.roles import ADMIN, PRODUCT_MANAGER
from app.schemas.catalog import PriceHistoryOut, PriceIn, ProductOut
from app.services.audit import log_action
from app.utils import get_or_404

router = APIRouter(prefix="/products", tags=["12. Pricing"])


# ---------------- pricing ----------------
@router.put("/{product_id}/price", response_model=ProductOut)
def change_price(product_id: int, data: PriceIn, db: Session = Depends(get_db),
                 me: User = Depends(require_roles(ADMIN, PRODUCT_MANAGER))):
    p = get_or_404(db, Product, product_id, "Product")
    new_base = data.base_price if data.base_price is not None else p.base_price
    new_sale = None if data.remove_sale else (data.sale_price if data.sale_price is not None else p.sale_price)
    start = data.sale_start if data.sale_start is not None else p.sale_start
    end = data.sale_end if data.sale_end is not None else p.sale_end

    if new_sale is not None and Decimal(new_sale) >= Decimal(new_base):
        raise HTTPException(400, "Sale price must be lower than base price")
    if start and end and end <= start:
        raise HTTPException(400, "Sale end must be after start")
    # big jumps are usually typos
    if Decimal(new_base) > Decimal(p.base_price) * 5 or Decimal(new_base) < Decimal(p.base_price) / 5:
        raise HTTPException(400, "Price change is more than 5x - double check the value")

    db.add(PriceHistory(product_id=p.id, old_base=p.base_price, new_base=new_base,
                        old_sale=p.sale_price, new_sale=new_sale, changed_by=me.id))
    log_action(db, me.id, "product.price_change", "product", p.id,
               {"base": p.base_price, "sale": p.sale_price}, {"base": new_base, "sale": new_sale})
    p.base_price, p.sale_price = new_base, new_sale
    p.sale_start, p.sale_end = (None, None) if data.remove_sale else (start, end)
    db.commit()
    return p


@router.get("/{product_id}/price-history", response_model=list[PriceHistoryOut])
def price_history(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    get_or_404(db, Product, product_id, "Product")
    return db.query(PriceHistory).filter_by(product_id=product_id).order_by(PriceHistory.id.desc()).all()