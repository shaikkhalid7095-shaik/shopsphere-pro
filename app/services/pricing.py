"""All money maths for cart / checkout. Prices are always read from the DB, never from the client."""
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import or_

from app.models import Coupon, Promotion, ShippingMethod, TaxRate
from app.services.stock import total_available
from app.utils import money, now


def effective_price(product, variant=None, at=None) -> Decimal:
    at = at or now()
    if variant is not None and variant.price is not None:
        return money(variant.price)
    if product.sale_price is not None:
        start_ok = product.sale_start is None or product.sale_start <= at
        end_ok = product.sale_end is None or product.sale_end >= at
        if start_ok and end_ok:
            return money(product.sale_price)
    return money(product.base_price)


def best_promotion(db, product, qty, at=None):
    at = at or now()
    promos = db.query(Promotion).filter(
        Promotion.is_active.is_(True),
        Promotion.start_at <= at,
        Promotion.end_at >= at,
        or_(Promotion.product_id == product.id, Promotion.category_id == product.category_id),
    ).all()
    best, best_off = None, Decimal("0")
    for p in promos:
        if qty < (p.min_quantity or 1):
            continue
        off = promo_unit_discount(p, effective_price(product))
        if off > best_off:
            best, best_off = p, off
    return best


def promo_unit_discount(promo, unit_price) -> Decimal:
    if promo.discount_type == "percent":
        off = unit_price * Decimal(promo.value) / 100
    else:
        off = Decimal(promo.value)
    return money(min(off, unit_price))


def validate_coupon(db, code, subtotal):
    coupon = db.query(Coupon).filter(Coupon.code == code.upper()).first()
    if not coupon or not coupon.is_active:
        raise HTTPException(400, "Invalid coupon code")
    t = now()
    if coupon.valid_from and coupon.valid_from > t:
        raise HTTPException(400, "Coupon is not active yet")
    if coupon.valid_to and coupon.valid_to < t:
        raise HTTPException(400, "Coupon has expired")
    if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
        raise HTTPException(400, "Coupon usage limit reached")
    if subtotal < money(coupon.min_purchase):
        raise HTTPException(400, f"Minimum purchase of {coupon.min_purchase} required for this coupon")
    return coupon


def coupon_discount(coupon, amount) -> Decimal:
    if coupon.discount_type == "percent":
        off = amount * Decimal(coupon.value) / 100
        if coupon.max_discount is not None:
            off = min(off, Decimal(coupon.max_discount))
    else:
        off = Decimal(coupon.value)
    return money(min(off, amount))


def tax_rate_for(db, product):
    rates = db.query(TaxRate).filter(TaxRate.is_active.is_(True)).all()
    for r in rates:
        if r.product_id == product.id:
            return r
    for r in rates:
        if r.category_id == product.category_id and r.product_id is None:
            return r
    for r in rates:
        if r.product_id is None and r.category_id is None:
            return r
    return None


def shipping_charge(method, subtotal, item_count, country=None) -> Decimal:
    if not method.is_active:
        raise HTTPException(400, "Shipping method is not available")
    if method.allowed_countries and country:
        allowed = [c.strip().lower() for c in method.allowed_countries.split(",") if c.strip()]
        if country.lower() not in allowed:
            raise HTTPException(400, f"{method.name} does not deliver to {country}")
    if method.max_items and item_count > method.max_items:
        raise HTTPException(400, f"{method.name} allows at most {method.max_items} items")
    if method.free_above is not None and subtotal >= money(method.free_above):
        return money(0)
    return money(Decimal(method.base_charge or 0) + Decimal(method.per_item_charge or 0) * item_count)


def calculate(db, lines, coupon_code=None, shipping_method_id=None, country=None, check_stock=True):
    """
    lines = list of (product, variant, qty)
    returns a full summary dict used by the cart summary and the checkout.
    """
    if not lines:
        raise HTTPException(400, "Cart is empty")

    result_lines = []
    subtotal = Decimal("0")
    promo_total = Decimal("0")
    problems = []

    for product, variant, qty in lines:
        if not product.is_active or (variant is not None and not variant.is_active):
            problems.append(f"{product.name} is no longer available")
            continue
        if check_stock:
            avail = total_available(db, product.id, variant.id if variant else None)
            if avail < qty:
                problems.append(f"Only {avail} left for {product.name}")
        unit = effective_price(product, variant)
        promo = best_promotion(db, product, qty)
        unit_off = promo_unit_discount(promo, unit) if promo else Decimal("0")
        gross = money(unit * qty)
        promo_off = money(unit_off * qty)
        subtotal += gross
        promo_total += promo_off
        result_lines.append({
            "product": product, "variant": variant, "quantity": qty,
            "unit_price": unit, "gross": gross, "discount": promo_off,
            "promotion": promo.name if promo else None,
        })

    if problems:
        raise HTTPException(409, {"message": "Some cart items have problems", "problems": problems})

    after_promo = subtotal - promo_total
    coupon_off = Decimal("0")
    if coupon_code:
        coupon = validate_coupon(db, coupon_code, after_promo)
        coupon_off = coupon_discount(coupon, after_promo)

    # spread the coupon over lines so tax is charged on the discounted amount
    tax_total = Decimal("0")
    breakdown = {}
    remaining = coupon_off
    for i, line in enumerate(result_lines):
        net = line["gross"] - line["discount"]
        if coupon_off and after_promo > 0:
            share = remaining if i == len(result_lines) - 1 else money(coupon_off * net / after_promo)
            remaining -= share
            line["discount"] += share
            net -= share
        rate = tax_rate_for(db, line["product"])
        line_tax = money(net * Decimal(rate.rate) / 100) if rate else Decimal("0")
        line["tax"] = line_tax
        line["line_total"] = money(net + line_tax)
        tax_total += line_tax
        if rate:
            key = f"{rate.name} ({rate.rate}%)"
            breakdown[key] = str(money(Decimal(breakdown.get(key, 0)) + line_tax))

    item_count = sum(line["quantity"] for line in result_lines)
    ship = Decimal("0")
    method = None
    if shipping_method_id:
        method = db.get(ShippingMethod, shipping_method_id)
        if not method:
            raise HTTPException(404, "Shipping method not found")
        ship = shipping_charge(method, after_promo - coupon_off, item_count, country)

    discount_total = promo_total + coupon_off
    grand = money(subtotal - discount_total + tax_total + ship)
    return {
        "lines": result_lines,
        "subtotal": money(subtotal),
        "promotion_discount": money(promo_total),
        "coupon_discount": money(coupon_off),
        "discount_total": money(discount_total),
        "tax_total": money(tax_total),
        "tax_breakdown": breakdown,
        "shipping_total": ship,
        "shipping_method": method.name if method else None,
        "grand_total": grand,
        "item_count": item_count,
    }