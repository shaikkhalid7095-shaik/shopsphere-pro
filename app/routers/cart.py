# Module 17 cart, 18 cart price calculation, 19 wishlist
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_customer
from app.models import Address, Cart, CartItem, Product, ProductVariant, User, WishlistItem
from app.schemas.common import Message
from app.schemas.sales import (CartAddIn, CartOut, CartQtyIn, SummaryIn, SummaryOut, WishlistIn,
                               WishlistOut)
from app.services.pricing import calculate, effective_price
from app.services.stock import total_available
from app.utils import money

router = APIRouter(tags=["17. Cart, 18. Cart Pricing, 19. Wishlist"])


def get_cart(db, user):
    cart = db.query(Cart).filter_by(user_id=user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
    return cart


def cart_lines(cart):
    return [(i.product, i.variant, i.quantity) for i in cart.items]


def variant_label(variant):
    return " / ".join(x for x in [variant.size, variant.color] if x) or variant.sku


def cart_view(db, cart):
    items, subtotal, count = [], money(0), 0
    for i in cart.items:
        unit = effective_price(i.product, i.variant)
        avail = total_available(db, i.product_id, i.variant_id)
        line = money(unit * i.quantity)
        subtotal += line
        count += i.quantity
        items.append({
            "id": i.id, "product_id": i.product_id, "variant_id": i.variant_id,
            "name": i.product.name + (f" ({variant_label(i.variant)})" if i.variant else ""),
            "sku": i.variant.sku if i.variant else i.product.sku,
            "unit_price": unit, "quantity": i.quantity, "line_total": line,
            "available": avail, "in_stock": avail >= i.quantity and i.product.is_active,
        })
    return CartOut(id=cart.id, items=items, item_count=count, subtotal=subtotal, coupon_code=cart.coupon_code)


@router.get("/cart", response_model=CartOut)
def view_cart(user: User = Depends(require_customer), db: Session = Depends(get_db)):
    cart = get_cart(db, user)
    db.commit()
    return cart_view(db, cart)


@router.post("/cart/items", response_model=CartOut)
def add_to_cart(data: CartAddIn, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    product = db.get(Product, data.product_id)
    if not product or not product.is_active:
        raise HTTPException(404, "Product not available")
    variant = None
    if data.variant_id:
        variant = db.get(ProductVariant, data.variant_id)
        if not variant or variant.product_id != product.id or not variant.is_active:
            raise HTTPException(400, "Invalid variant for this product")
    elif product.variants and any(v.is_active for v in product.variants):
        raise HTTPException(400, "Please choose a variant (size/color) for this product")

    cart = get_cart(db, user)
    existing = next((i for i in cart.items if i.product_id == product.id and i.variant_id == data.variant_id), None)
    new_qty = data.quantity + (existing.quantity if existing else 0)
    avail = total_available(db, product.id, data.variant_id)
    if new_qty > avail:
        raise HTTPException(400, f"Only {avail} in stock")
    if existing:
        existing.quantity = new_qty
    else:
        cart.items.append(CartItem(product_id=product.id, variant_id=data.variant_id, quantity=data.quantity))
    db.commit()
    db.refresh(cart)
    return cart_view(db, cart)


@router.put("/cart/items/{item_id}", response_model=CartOut)
def update_cart_item(item_id: int, data: CartQtyIn, user: User = Depends(require_customer),
                     db: Session = Depends(get_db)):
    cart = get_cart(db, user)
    item = next((i for i in cart.items if i.id == item_id), None)
    if not item:
        raise HTTPException(404, "Item not in your cart")
    avail = total_available(db, item.product_id, item.variant_id)
    if data.quantity > avail:
        raise HTTPException(400, f"Only {avail} in stock")
    item.quantity = data.quantity
    db.commit()
    return cart_view(db, cart)


@router.delete("/cart/items/{item_id}", response_model=CartOut)
def remove_cart_item(item_id: int, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    cart = get_cart(db, user)
    item = next((i for i in cart.items if i.id == item_id), None)
    if not item:
        raise HTTPException(404, "Item not in your cart")
    cart.items.remove(item)
    db.commit()
    db.refresh(cart)
    return cart_view(db, cart)


@router.delete("/cart", response_model=Message)
def clear_cart(user: User = Depends(require_customer), db: Session = Depends(get_db)):
    cart = get_cart(db, user)
    cart.items.clear()
    cart.coupon_code = None
    db.commit()
    return {"message": "Cart cleared"}


def summary_to_out(summary):
    lines = []
    for line in summary["lines"]:
        lines.append({
            "product_id": line["product"].id, "variant_id": line["variant"].id if line["variant"] else None,
            "name": line["product"].name, "quantity": line["quantity"], "unit_price": line["unit_price"],
            "discount": line["discount"], "tax": line["tax"], "line_total": line["line_total"],
            "promotion": line["promotion"],
        })
    data = {k: v for k, v in summary.items() if k != "lines"}
    return SummaryOut(lines=lines, **data)


@router.post("/cart/summary", response_model=SummaryOut)
def cart_summary(data: SummaryIn, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    """recalculates everything from current DB prices - this is what checkout will charge"""
    cart = get_cart(db, user)
    country = None
    if data.shipping_address_id:
        addr = db.get(Address, data.shipping_address_id)
        if not addr or addr.user_id != user.id or addr.is_deleted:
            raise HTTPException(404, "Address not found")
        country = addr.country
    summary = calculate(db, cart_lines(cart), data.coupon_code, data.shipping_method_id, country)
    if data.coupon_code:
        cart.coupon_code = data.coupon_code.upper()
        db.commit()
    return summary_to_out(summary)


# ---------------- wishlist ----------------
def wishlist_view(db, rows):
    return [WishlistOut(id=w.id, product_id=w.product_id, name=w.product.name, price=effective_price(w.product),
                        available=total_available(db, w.product_id, None) + sum(
                            total_available(db, w.product_id, v.id) for v in w.product.variants),
                        is_active=w.product.is_active, added_at=w.added_at) for w in rows]


@router.get("/wishlist", response_model=list[WishlistOut])
def my_wishlist(user: User = Depends(require_customer), db: Session = Depends(get_db)):
    rows = db.query(WishlistItem).filter_by(user_id=user.id).order_by(WishlistItem.id.desc()).all()
    return wishlist_view(db, rows)


@router.post("/wishlist", response_model=list[WishlistOut], status_code=201)
def add_wishlist(data: WishlistIn, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    product = db.get(Product, data.product_id)
    if not product or not product.is_active:
        raise HTTPException(404, "Product not available")
    if db.query(WishlistItem).filter_by(user_id=user.id, product_id=product.id).first():
        raise HTTPException(409, "Already in your wishlist")
    db.add(WishlistItem(user_id=user.id, product_id=product.id))
    db.commit()
    return my_wishlist(user, db)


@router.delete("/wishlist/{product_id}", status_code=204)
def remove_wishlist(product_id: int, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    row = db.query(WishlistItem).filter_by(user_id=user.id, product_id=product_id).first()
    if not row:
        raise HTTPException(404, "Not in wishlist")
    db.delete(row)
    db.commit()