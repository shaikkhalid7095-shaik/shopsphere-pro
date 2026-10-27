"""Unit tests - pure business logic, no HTTP."""
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.security import create_access_token, decode_token, hash_password, verify_password
from app.services.orders import can_move
from app.services.pricing import coupon_discount, effective_price, promo_unit_discount, shipping_charge
from app.utils import now


def test_password_hash_and_verify():
    h = hash_password("Secret123")
    assert h != "Secret123"
    assert verify_password("Secret123", h)
    assert not verify_password("wrong", h)


def test_jwt_round_trip():
    token, jti, _ = create_access_token(7, "customer")
    payload = decode_token(token)
    assert payload["sub"] == "7"
    assert payload["role"] == "customer"
    assert payload["type"] == "access"
    assert payload["jti"] == jti


@pytest.mark.parametrize("current,new,ok", [
    ("pending", "confirmed", True),
    ("pending", "shipped", False),
    ("confirmed", "processing", True),
    ("processing", "shipped", True),
    ("shipped", "delivered", True),
    ("delivered", "cancelled", False),
    ("cancelled", "confirmed", False),
    ("shipped", "cancelled", False),
])
def test_order_status_transitions(current, new, ok):
    assert can_move(current, new) is ok


def _product(base, sale=None, start=None, end=None):
    return SimpleNamespace(base_price=Decimal(base), sale_price=Decimal(sale) if sale else None,
                           sale_start=start, sale_end=end)


def test_effective_price_uses_sale_only_inside_window():
    t = now()
    assert effective_price(_product("1000")) == Decimal("1000.00")
    assert effective_price(_product("1000", "800")) == Decimal("800.00")
    assert effective_price(_product("1000", "800", start=t + timedelta(days=1))) == Decimal("1000.00")
    assert effective_price(_product("1000", "800", end=t - timedelta(days=1))) == Decimal("1000.00")


def test_variant_price_overrides_product():
    v = SimpleNamespace(price=Decimal("1200"))
    assert effective_price(_product("1000", "800"), v) == Decimal("1200.00")


def test_coupon_percent_with_cap_and_fixed():
    pct = SimpleNamespace(discount_type="percent", value=Decimal("10"), max_discount=Decimal("50"))
    assert coupon_discount(pct, Decimal("300")) == Decimal("30.00")
    assert coupon_discount(pct, Decimal("1000")) == Decimal("50.00")
    fixed = SimpleNamespace(discount_type="fixed", value=Decimal("500"), max_discount=None)
    # never more than the amount
    assert coupon_discount(fixed, Decimal("200")) == Decimal("200.00")


def test_promotion_unit_discount():
    promo = SimpleNamespace(discount_type="percent", value=Decimal("25"))
    assert promo_unit_discount(promo, Decimal("400")) == Decimal("100.00")


def test_shipping_rules():
    m = SimpleNamespace(name="Std", is_active=True, allowed_countries="India", max_items=5,
                        base_charge=Decimal("49"), per_item_charge=Decimal("10"), free_above=Decimal("999"))
    assert shipping_charge(m, Decimal("500"), 2, "India") == Decimal("69.00")
    assert shipping_charge(m, Decimal("1500"), 2, "India") == Decimal("0.00")
    with pytest.raises(HTTPException):
        shipping_charge(m, Decimal("500"), 2, "USA")
    with pytest.raises(HTTPException):
        shipping_charge(m, Decimal("500"), 9, "India")