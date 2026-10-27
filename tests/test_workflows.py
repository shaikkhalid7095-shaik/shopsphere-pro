"""Integration tests: real DB + HTTP for the main shopping workflows."""
from decimal import Decimal

import pytest

from app.database import SessionLocal
from app.models import AuditLog


def product_id(client, sku):
    r = client.get("/products", params={"search": sku})
    return r.json()["items"][0]["id"]


def available(client, auth, pid):
    return client.get(f"/inventory/product/{pid}", headers=auth("admin")).json()["available"]


def address_id(client, auth, who="customer"):
    return client.get("/addresses", headers=auth(who)).json()[0]["id"]


def shipping_id(client, code="STANDARD"):
    return next(m["id"] for m in client.get("/shipping-methods").json() if m["code"] == code)


def place_order(client, auth, sku, qty, method="card", key=None, coupon=None, who="customer"):
    h = auth(who)
    client.delete("/cart", headers=h)
    r = client.post("/cart/items", json={"product_id": product_id(client, sku), "quantity": qty}, headers=h)
    assert r.status_code == 200, r.text
    headers = dict(h)
    if key:
        headers["Idempotency-Key"] = key
    body = {"shipping_address_id": address_id(client, auth, who), "shipping_method_id": shipping_id(client),
            "payment_method": method, "coupon_code": coupon}
    return client.post("/checkout", json=body, headers=headers)


def pay(client, auth, order_id, who="customer"):
    intent = client.post(f"/payments/orders/{order_id}/intent", headers=auth(who))
    assert intent.status_code in (200, 201), intent.text
    sim = client.post(f"/payments/sandbox/{intent.json()['gateway_ref']}/simulate", params={"outcome": "success"},
                      headers=auth(who))
    assert sim.status_code == 200, sim.text
    return intent.json(), sim.json()


def test_cart_summary_uses_server_prices(client, auth):
    h = auth("customer")
    client.delete("/cart", headers=h)
    client.post("/cart/items", json={"product_id": product_id(client, "SAM-M14"), "quantity": 2}, headers=h)
    r = client.post("/cart/summary", json={"coupon_code": "WELCOME10", "shipping_method_id": shipping_id(client)},
                    headers=h)
    assert r.status_code == 200, r.text
    s = r.json()
    assert Decimal(s["subtotal"]) == Decimal("25998.00")        # sale price 12999 x 2
    assert Decimal(s["coupon_discount"]) == Decimal("500.00")   # 10% capped at 500
    assert Decimal(s["tax_total"]) == Decimal("4589.64")        # 18% on 25498
    assert Decimal(s["shipping_total"]) == Decimal("0.00")      # free above 999
    assert Decimal(s["grand_total"]) == Decimal("30087.64")


def test_cart_rejects_more_than_stock(client, auth):
    h = auth("customer")
    r = client.post("/cart/items", json={"product_id": product_id(client, "BOAT-AIR141"), "quantity": 50}, headers=h)
    r = client.post("/cart/items", json={"product_id": product_id(client, "BOAT-AIR141"), "quantity": 50}, headers=h)
    assert r.status_code in (200, 400)
    r = client.post("/cart/items", json={"product_id": product_id(client, "BOAT-AIR141"), "quantity": 50}, headers=h)
    assert r.status_code == 400


def test_variant_required_for_tshirt(client, auth):
    r = client.post("/cart/items", json={"product_id": product_id(client, "UW-TEE-BASIC"), "quantity": 1},
                    headers=auth("customer"))
    assert r.status_code == 400


def test_full_card_order_lifecycle(client, auth):
    pid = product_id(client, "SAM-M14")
    before = available(client, auth, pid)

    # --- checkout is idempotent ---
    r1 = place_order(client, auth, "SAM-M14", 2, key="order-key-1", coupon="WELCOME10")
    assert r1.status_code == 201, r1.text
    order = r1.json()
    assert order["status"] == "pending" and order["payment_status"] == "unpaid"
    assert len(order["items"]) == 1 and order["items"][0]["sku"] == "SAM-M14"
    r2 = client.post("/checkout", json={"shipping_address_id": address_id(client, auth),
                                        "shipping_method_id": shipping_id(client)},
                     headers={**auth("customer"), "Idempotency-Key": "order-key-1"})
    assert r2.status_code == 200 and r2.json()["id"] == order["id"]
    assert available(client, auth, pid) == before - 2   # reserved

    # --- payment can't be created twice ---
    i1 = client.post(f"/payments/orders/{order['id']}/intent", headers=auth("customer")).json()
    i2 = client.post(f"/payments/orders/{order['id']}/intent", headers=auth("customer")).json()
    assert i1["id"] == i2["id"] and i2["is_existing"] is True

    sim = client.post(f"/payments/sandbox/{i1['gateway_ref']}/simulate", headers=auth("customer")).json()
    assert sim["status"] == "processed"
    # the same webhook again is ignored
    dup = client.post("/payments/webhook", content=sim["raw_body"],
                      headers={"X-Sandbox-Signature": sim["signature"], "Content-Type": "application/json"})
    assert dup.json()["status"] == "duplicate_ignored"
    bad = client.post("/payments/webhook", content=b'{"id":"x"}', headers={"X-Sandbox-Signature": "wrong"})
    assert bad.status_code == 400

    o = client.get(f"/orders/{order['id']}", headers=auth("customer")).json()
    assert o["status"] == "confirmed" and o["payment_status"] == "paid"
    assert client.post(f"/payments/orders/{order['id']}/intent", headers=auth("customer")).status_code == 409

    # --- other customers can't see it ---
    assert client.get(f"/orders/{order['id']}", headers=auth("customer2")).status_code == 404
    ids = [x["id"] for x in client.get("/orders", headers=auth("customer2")).json()["items"]]
    assert order["id"] not in ids

    # --- customer can't push status ---
    assert client.put(f"/orders/{order['id']}/status", json={"status": "shipped"},
                      headers=auth("customer")).status_code == 403

    # --- shipping ---
    provider = client.get("/shipping-providers", headers=auth("order_manager")).json()[0]["id"]
    s = client.post("/shipments", json={"order_id": order["id"], "provider_id": provider},
                    headers=auth("order_manager"))
    assert s.status_code == 201, s.text
    shipment = s.json()
    d = client.post(f"/shipments/{shipment['id']}/dispatch", headers=auth("order_manager"))
    assert d.status_code == 200, d.text
    stock_row = client.get(f"/inventory/product/{pid}", headers=auth("admin")).json()
    assert stock_row["reserved"] == 0

    t = client.post(f"/shipments/{shipment['id']}/tracking", json={"status": "in_transit", "location": "Pune"},
                    headers=auth("delivery_manager"))
    assert t.status_code == 200
    track = client.get(f"/shipments/track/{shipment['tracking_number']}", headers=auth("customer"))
    assert track.json()["status"] == "in_transit"

    # --- delivery ---
    delivery_user = client.get("/users", params={"role": "delivery_manager"}, headers=auth("admin")).json()["items"][0]
    a = client.post(f"/shipments/{shipment['id']}/assign", json={"assigned_to": delivery_user["id"]},
                    headers=auth("delivery_manager")).json()
    client.post(f"/deliveries/{a['id']}/attempts", json={"result": "failed", "reason": "Door locked"},
                headers=auth("delivery_manager"))
    done = client.post(f"/deliveries/{a['id']}/attempts", json={"result": "delivered", "receiver_name": "Ravi"},
                       headers=auth("delivery_manager"))
    assert done.status_code == 200 and done.json()["attempts"] == 2
    o = client.get(f"/orders/{order['id']}", headers=auth("customer")).json()
    assert o["status"] == "delivered"
    assert [h["to_status"] for h in o["history"]] == ["pending", "confirmed", "processing", "shipped", "delivered"]

    # --- review (verified purchase only, one per product) ---
    rv = {"product_id": pid, "rating": 5, "comment": "Great phone"}
    assert client.post("/reviews", json=rv, headers=auth("customer")).status_code == 201
    assert client.post("/reviews", json=rv, headers=auth("customer")).status_code == 409
    assert client.post("/reviews", json=rv, headers=auth("customer2")).status_code == 403
    assert client.get(f"/products/{pid}/rating").json()["average"] == 5.0

    # --- return one unit -> refund ---
    item_id = o["items"][0]["id"]
    ret = client.post("/returns", json={"order_id": order["id"], "reason": "Changed mind",
                                        "items": [{"order_item_id": item_id, "quantity": 1}]},
                      headers=auth("customer"))
    assert ret.status_code == 201, ret.text
    rid = ret.json()["id"]
    assert client.post(f"/returns/{rid}/review", json={"approve": True}, headers=auth("order_manager")).status_code == 200
    wh = client.get("/warehouses", headers=auth("admin")).json()[0]["id"]
    rec = client.post(f"/returns/{rid}/receive", json={"warehouse_id": wh}, headers=auth("order_manager"))
    assert rec.status_code == 200, rec.text
    assert rec.json()["status"] == "refunded"
    o = client.get(f"/orders/{order['id']}", headers=auth("customer")).json()
    assert o["payment_status"] == "partially_refunded"
    # can't return more than bought
    over = client.post("/returns", json={"order_id": order["id"], "reason": "again",
                                         "items": [{"order_item_id": item_id, "quantity": 2}]},
                       headers=auth("customer"))
    assert over.status_code == 400


def test_cancel_paid_order_refunds_and_releases_stock(client, auth):
    pid = product_id(client, "BOAT-AIR141")
    client.delete("/cart", headers=auth("customer"))
    before = available(client, auth, pid)
    order = place_order(client, auth, "BOAT-AIR141", 1).json()
    assert available(client, auth, pid) == before - 1
    pay(client, auth, order["id"])

    r = client.post(f"/orders/{order['id']}/cancel", json={"reason": "Ordered by mistake"}, headers=auth("customer"))
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "cancelled"
    assert r.json()["payment_status"] == "refunded"
    assert available(client, auth, pid) == before
    info = client.get(f"/orders/{order['id']}/cancellation", headers=auth("customer")).json()
    assert "refund" in info["outcome"].lower()
    # second cancel is rejected
    again = client.post(f"/orders/{order['id']}/cancel", json={"reason": "again"}, headers=auth("customer"))
    assert again.status_code == 409


def test_failed_payment(client, auth):
    order = place_order(client, auth, "BOAT-AIR141", 1).json()
    intent = client.post(f"/payments/orders/{order['id']}/intent", headers=auth("customer")).json()
    sim = client.post(f"/payments/sandbox/{intent['gateway_ref']}/simulate", params={"outcome": "fail"},
                      headers=auth("customer")).json()
    assert sim["payment_status"] == "failed"
    o = client.get(f"/orders/{order['id']}", headers=auth("customer")).json()
    assert o["payment_status"] == "failed" and o["status"] == "pending"
    # retry creates a fresh payment
    retry = client.post(f"/payments/orders/{order['id']}/intent", headers={**auth("customer"),
                                                                           "Idempotency-Key": "retry-1"})
    assert retry.status_code == 201 and retry.json()["id"] != intent["id"]


def test_cod_flow(client, auth):
    order = place_order(client, auth, "BOAT-AIR141", 1, method="cod").json()
    assert order["payment_status"] == "cod_pending"
    oid = order["id"]
    early = client.post(f"/cod/collections/{oid}/collect", json={"amount": order["grand_total"]},
                        headers=auth("delivery_manager"))
    assert early.status_code == 400  # not shipped yet
    client.put(f"/orders/{oid}/status", json={"status": "confirmed"}, headers=auth("order_manager"))
    client.put(f"/orders/{oid}/status", json={"status": "processing"}, headers=auth("order_manager"))
    assert client.put(f"/orders/{oid}/status", json={"status": "shipped"},
                      headers=auth("order_manager")).status_code == 200
    col = client.post(f"/cod/collections/{oid}/collect", json={"amount": order["grand_total"]},
                      headers=auth("delivery_manager"))
    assert col.status_code == 200 and col.json()["status"] == "collected"
    dup = client.post(f"/cod/collections/{oid}/collect", json={"amount": order["grand_total"]},
                      headers=auth("delivery_manager"))
    assert dup.status_code == 409
    rec = client.post(f"/cod/collections/{oid}/reconcile", json={}, headers=auth("finance_manager"))
    assert rec.json()["status"] == "reconciled"


def test_invalid_status_jump(client, auth):
    order = place_order(client, auth, "BOAT-AIR141", 1, method="cod").json()
    r = client.put(f"/orders/{order['id']}/status", json={"status": "delivered"}, headers=auth("order_manager"))
    assert r.status_code == 400


def test_inventory_never_negative(client, auth):
    pid = product_id(client, "BOAT-AIR141")
    wh = client.get("/warehouses", headers=auth("admin")).json()[0]["id"]
    r = client.post("/inventory/adjust", json={"product_id": pid, "warehouse_id": wh, "quantity": 99999,
                                               "action": "remove"}, headers=auth("inventory_manager"))
    assert r.status_code == 400
    ok = client.post("/inventory/adjust", json={"product_id": pid, "warehouse_id": wh, "quantity": 5,
                                                "action": "add"}, headers=auth("inventory_manager"))
    assert ok.status_code == 200
    assert client.post("/inventory/adjust", json={"product_id": pid, "warehouse_id": wh, "quantity": 5,
                                                  "action": "add"}, headers=auth("customer")).status_code == 403


def test_warehouse_transfer(client, auth):
    pid = product_id(client, "SAM-M14")
    whs = client.get("/warehouses", headers=auth("admin")).json()
    src, dst = whs[0]["id"], whs[1]["id"]
    t = client.post("/inventory/transfers", json={"from_warehouse_id": src, "to_warehouse_id": dst,
                                                  "product_id": pid, "quantity": 5},
                    headers=auth("inventory_manager")).json()
    assert client.post(f"/inventory/transfers/{t['id']}/receive", json={"quantity": 5},
                       headers=auth("inventory_manager")).status_code == 400  # not dispatched yet
    assert client.post(f"/inventory/transfers/{t['id']}/dispatch", json={"quantity": 5},
                       headers=auth("inventory_manager")).status_code == 200
    r = client.post(f"/inventory/transfers/{t['id']}/receive", json={"quantity": 5}, headers=auth("inventory_manager"))
    assert r.json()["status"] == "received"


def test_coupon_validation(client, auth):
    h = auth("customer")
    client.delete("/cart", headers=h)
    client.post("/cart/items", json={"product_id": product_id(client, "BOAT-AIR141"), "quantity": 1}, headers=h)
    r = client.post("/cart/summary", json={"coupon_code": "FLAT100"}, headers=h)   # min purchase 999
    assert r.status_code == 200
    r = client.post("/cart/summary", json={"coupon_code": "NOPE"}, headers=h)
    assert r.status_code == 400


def test_promotion_applies_for_min_quantity(client, auth):
    h = auth("customer")
    tee = client.get(f"/products/{product_id(client, 'UW-TEE-BASIC')}").json()
    v = tee["variants"][0]["id"]
    client.delete("/cart", headers=h)
    client.post("/cart/items", json={"product_id": tee["id"], "variant_id": v, "quantity": 2}, headers=h)
    s = client.post("/cart/summary", json={}, headers=h).json()
    assert Decimal(s["promotion_discount"]) == Decimal("119.80")   # 10% of 599 x 2
    assert s["lines"][0]["promotion"] == "T-Shirt Fest"


def test_audit_logs_are_read_only(client, auth):
    logs = client.get("/audit-logs", headers=auth("admin")).json()
    assert logs["total"] > 0
    db = SessionLocal()
    try:
        row = db.query(AuditLog).first()
        row.action = "tampered"
        with pytest.raises(ValueError):
            db.commit()
        db.rollback()
    finally:
        db.close()


def test_dashboard_is_role_based(client, auth):
    admin = client.get("/dashboard", headers=auth("admin")).json()
    assert {"products", "inventory", "orders_by_status", "revenue"} <= set(admin)
    inv = client.get("/dashboard", headers=auth("inventory_manager")).json()
    assert "inventory" in inv and "revenue" not in inv
    assert client.get("/dashboard", headers=auth("customer")).status_code == 403


@pytest.mark.parametrize("fmt", ["csv", "xlsx", "pdf"])
def test_report_export_job(client, auth, fmt):
    r = client.post("/reports/export", json={"report": "sales", "format": fmt}, headers=auth("finance_manager"))
    assert r.status_code == 202
    job = client.get(f"/jobs/{r.json()['id']}", headers=auth("finance_manager")).json()
    assert job["status"] == "success", job
    dl = client.get(f"/jobs/{job['id']}/download", headers=auth("finance_manager"))
    assert dl.status_code == 200 and len(dl.content) > 0


def test_notifications_and_outbox(client, auth):
    n = client.get("/notifications", headers=auth("customer")).json()
    assert n["total"] > 0
    client.put("/notifications/read-all", headers=auth("customer"))
    assert client.get("/notifications/unread-count", headers=auth("customer")).json()["unread"] == 0
    processed = client.post("/messaging/process", headers=auth("admin")).json()["processed"]
    assert processed >= 0
    sent = client.get("/messaging/outbox", params={"status": "sent"}, headers=auth("admin")).json()
    assert sent["total"] > 0


def test_support_ticket_flow(client, auth):
    t = client.post("/tickets", json={"subject": "Where is my order", "message": "Not received yet"},
                    headers=auth("customer")).json()
    agent = client.get("/users", params={"role": "support_agent"}, headers=auth("admin")).json()["items"][0]
    assert client.put(f"/tickets/{t['id']}/assign", json={"agent_id": agent["id"]},
                      headers=auth("support_agent")).status_code == 200
    client.post(f"/tickets/{t['id']}/messages", json={"message": "internal note", "is_internal": True},
                headers=auth("support_agent"))
    seen = client.get(f"/tickets/{t['id']}", headers=auth("customer")).json()
    assert all(not m["is_internal"] for m in seen["messages"])  # customer never sees internal notes
    assert client.get(f"/tickets/{t['id']}", headers=auth("customer2")).status_code == 404
    bad = client.patch(f"/tickets/{t['id']}", json={"status": "resolved"}, headers=auth("support_agent"))
    assert bad.status_code == 400
    ok = client.patch(f"/tickets/{t['id']}", json={"status": "resolved", "resolution": "Shipped today"},
                      headers=auth("support_agent"))
    assert ok.json()["status"] == "resolved"


def test_supplier_po_invoice_flow(client, auth):
    sup = client.post("/suppliers", json={"name": "Acme", "email": "acme@test.com"}, headers=auth("inventory_manager"))
    sid = sup.json()["id"]
    wh = client.get("/warehouses", headers=auth("admin")).json()[0]["id"]
    pid = product_id(client, "BOAT-AIR141")
    po_body = {"supplier_id": sid, "warehouse_id": wh, "items": [{"product_id": pid, "quantity": 10, "unit_cost": "800"}]}
    assert client.post("/purchase-orders", json=po_body, headers=auth("inventory_manager")).status_code == 400
    client.put(f"/suppliers/{sid}/status", json={"status": "approved"}, headers=auth("admin"))
    po = client.post("/purchase-orders", json=po_body, headers=auth("inventory_manager")).json()
    client.post(f"/purchase-orders/{po['id']}/send", headers=auth("inventory_manager"))
    before = available(client, auth, pid)
    rec = client.post(f"/purchase-orders/{po['id']}/receive",
                      json={"lines": [{"po_item_id": po["items"][0]["id"], "quantity": 10}]},
                      headers=auth("inventory_manager")).json()
    assert rec["status"] == "received"
    assert available(client, auth, pid) == before + 10

    inv = {"po_id": po["id"], "invoice_number": "INV-001", "invoice_date": "2026-10-20", "amount": "8000"}
    assert client.post("/supplier-invoices", json=inv, headers=auth("finance_manager")).status_code == 201
    assert client.post("/supplier-invoices", json=inv, headers=auth("finance_manager")).status_code == 409
    inv_id = client.get("/supplier-invoices", headers=auth("finance_manager")).json()["items"][0]["id"]
    paid = client.post(f"/supplier-invoices/{inv_id}/pay", json={"amount": "8000"}, headers=auth("finance_manager"))
    assert paid.json()["status"] == "paid"