"""Auth, registration, role permissions and customer data isolation."""
from tests.conftest import login


def test_register_verify_and_login(client):
    data = {"full_name": "Test User", "email": "newbie@test.com", "phone": "9800000001", "password": "Hello1234"}
    r = client.post("/auth/register", json=data)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["registration_status"] == "pending_verification"

    r = client.get("/auth/verify-email", params={"token": body["verify_token"]})
    assert r.status_code == 200
    headers = login(client, "newbie@test.com", "Hello1234")
    me = client.get("/auth/me", headers=headers).json()
    assert me["is_email_verified"] is True
    assert me["role_name"] == "customer"


def test_duplicate_and_invalid_registration(client):
    dup = {"full_name": "Again", "email": "customer@shopsphere.com", "phone": "9800000002", "password": "Hello1234"}
    assert client.post("/auth/register", json=dup).status_code == 409
    bad_phone = {"full_name": "X Y", "email": "x@test.com", "phone": "12ab", "password": "Hello1234"}
    assert client.post("/auth/register", json=bad_phone).status_code == 422
    weak = {"full_name": "X Y", "email": "y@test.com", "phone": "9800000003", "password": "short"}
    assert client.post("/auth/register", json=weak).status_code == 422


def test_wrong_password(client):
    r = client.post("/auth/login", json={"email": "customer@shopsphere.com", "password": "nope"})
    assert r.status_code == 401


def test_refresh_rotation_and_logout(client):
    r = client.post("/auth/login", json={"email": "customer2@shopsphere.com", "password": "Password@123"})
    tokens = r.json()
    r2 = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r2.status_code == 200
    # old refresh token was rotated out
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401

    new = r2.json()
    h = {"Authorization": f"Bearer {new['access_token']}"}
    assert client.get("/auth/me", headers=h).status_code == 200
    assert client.post("/auth/logout", headers=h, json={"refresh_token": new["refresh_token"]}).status_code == 200
    assert client.get("/auth/me", headers=h).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": new["refresh_token"]}).status_code == 401


def test_no_token(client):
    assert client.get("/profile").status_code == 401


def test_role_permissions(client, auth):
    product = {"name": "RBAC Test", "sku": "RBAC-1", "category_id": 1, "base_price": "100"}
    assert client.post("/products", json=product, headers=auth("customer")).status_code == 403
    assert client.post("/products", json=product, headers=auth("support_agent")).status_code == 403
    assert client.post("/products", json=product, headers=auth("product_manager")).status_code == 201
    # super admin passes every role check
    assert client.get("/users", headers=auth("super_admin")).status_code == 200
    assert client.get("/users", headers=auth("customer")).status_code == 403
    assert client.get("/audit-logs", headers=auth("finance_manager")).status_code == 403
    assert client.get("/reports/sales", headers=auth("finance_manager")).status_code == 200


def test_admin_cannot_create_super_admin(client, auth):
    data = {"full_name": "Sneaky", "email": "sneaky@test.com", "password": "Hello1234", "role": "super_admin"}
    assert client.post("/users", json=data, headers=auth("admin")).status_code == 403


def test_address_isolation(client, auth):
    addr = {"full_name": "Meena", "phone": "9876543211", "line1": "12 MG Road", "city": "Bengaluru",
            "state": "Karnataka", "postal_code": "560001"}
    r = client.post("/addresses", json=addr, headers=auth("customer2"))
    assert r.status_code == 201
    addr_id = r.json()["id"]
    assert r.json()["is_default"] is True  # first one becomes default
    # other customer can't touch it
    assert client.put(f"/addresses/{addr_id}", json=addr, headers=auth("customer")).status_code == 404
    assert client.delete(f"/addresses/{addr_id}", headers=auth("customer")).status_code == 404


def test_profile_update_keeps_history(client, auth):
    r = client.patch("/profile", json={"full_name": "Meena K"}, headers=auth("customer2"))
    assert r.status_code == 200
    hist = client.get("/profile/history", headers=auth("customer2")).json()
    assert hist["items"][0]["field"] == "full_name"
    assert hist["items"][0]["new_value"] == "Meena K"