# ShopSphere Pro – E-Commerce Backend

FastAPI + MySQL + SQLAlchemy backend covering the full shopping lifecycle: registration → catalog → cart → checkout → payment → shipping → delivery → returns/refunds, plus suppliers, reports and background jobs.

**50 modules · 220 endpoints · 65 tables · JWT + RBAC (9 roles) · 44 automated tests · 131-request Postman collection**

| Piece | Used |
|---|---|
| Framework | FastAPI |
| Database / ORM | MySQL 8 + SQLAlchemy 2 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT access + refresh tokens (rotation + revocation) |
| Passwords | bcrypt |
| Payments | Stripe test mode, or the built-in sandbox gateway (default, works offline) |
| Exports | CSV, Excel (openpyxl), PDF (reportlab) |

---

## Quick start (Windows PowerShell)

You need **Python 3.10+** and **MySQL 8** running.

Open PowerShell in this folder and run:

```powershell
# 1. one-time setup (makes .venv, installs packages, creates DB, tables and sample data)
powershell -ExecutionPolicy Bypass -File .\setup.ps1

# 2. start the API (opens Swagger in your browser)
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

That's it. Swagger UI: **http://127.0.0.1:8000/docs**

`setup.ps1` asks for your MySQL username and password. To skip the questions:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1 -DbPassword yourMySqlPassword
```

Other scripts:

| Script | What it does |
|---|---|
| `.\test.ps1` | Runs all 44 tests on a temporary SQLite file (your data is safe) |
| `.\test.ps1 -MySql` | Runs the same tests on a separate `shopsphere_test` MySQL database |
| `.\reset-db.ps1` | Wipes all tables and reloads the sample data (asks first) |

> **Why `-ExecutionPolicy Bypass`?** Windows blocks scripts by default, especially ones from a downloaded zip. This flag allows it for that one run only. If you'd rather type `.\setup.ps1` directly, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and then `Get-ChildItem *.ps1 | Unblock-File`.

### Manual setup (if you don't want the scripts)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env        # then edit DB_PASSWORD in .env
python create_db.py
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

---

## Sample accounts

All passwords: **`Password@123`**

| Role | Email |
|---|---|
| Super Admin | superadmin@shopsphere.com |
| Admin | admin@shopsphere.com |
| Product Manager | products@shopsphere.com |
| Inventory Manager | inventory@shopsphere.com |
| Order Manager | orders@shopsphere.com |
| Support Agent | support@shopsphere.com |
| Delivery Manager | delivery@shopsphere.com |
| Finance Manager | finance@shopsphere.com |
| Customer | customer@shopsphere.com |
| Customer 2 | customer2@shopsphere.com |

Sample data also includes 3 products (a phone, earbuds, a T-shirt with 3 variants), 2 warehouses with stock, GST tax rules, 2 shipping methods, coupons `WELCOME10` and `FLAT100`, a "buy 2 T-shirts get 10% off" promotion, and 2 courier providers.

---

## Try the main flow in Swagger (5 minutes)

1. `POST /auth/login` as `customer@shopsphere.com` → copy `access_token` → click **Authorize** → paste.
2. `POST /cart/items` → `{"product_id": 1, "quantity": 2}`
3. `POST /cart/summary` → `{"coupon_code": "WELCOME10", "shipping_method_id": 1}` – see subtotal, discount, GST, shipping.
4. `POST /checkout` → `{"shipping_address_id": 1, "shipping_method_id": 1, "payment_method": "card"}` (add header `Idempotency-Key: anything` and send twice – you get the same order back).
5. `POST /payments/orders/{order_id}/intent` → copy `gateway_ref`.
6. `POST /payments/sandbox/{gateway_ref}/simulate?outcome=success` → order becomes **confirmed / paid**.
7. Log in as `orders@shopsphere.com` → `POST /shipments` `{"order_id": 1, "provider_id": 1}` → `POST /shipments/{id}/dispatch` → order **shipped**, stock deducted.
8. Log in as `delivery@shopsphere.com` → `POST /shipments/{id}/assign` `{"assigned_to": 7}` → `POST /deliveries/{id}/attempts` `{"result": "delivered", "receiver_name": "Ravi"}` → order **delivered**.
9. Back as customer → `POST /reviews`, `POST /returns`… then as order manager approve + receive → refund is processed automatically.

Or just import the Postman collection and run it (below) – it does all of this for you.

---

## Postman

Import `postman/ShopSphere_Pro.postman_collection.json`.

- Run folder **00 Setup** first – it logs in as every role and saves the tokens into collection variables.
- Then run the whole collection (Runner) in order. IDs (order, shipment, payment…) are passed between requests automatically.
- Includes negative checks: wrong password (401), customer creating a product (403), viewing another customer's order (404), duplicate registration (409), paying twice (409), invalid status jump (400), webhook replay ignored.

Run it on a **fresh database** (`.\reset-db.ps1`) – a few requests use the seeded IDs.

---

## Tests

```powershell
.\test.ps1            # sqlite, quick
.\test.ps1 -MySql     # real MySQL
```

- `tests/test_unit.py` – password hashing, JWT, order status rules, price/sale windows, coupons, promotions, shipping rules
- `tests/test_auth_rbac.py` – register/verify/login, refresh rotation, logout revocation, role permissions, data isolation
- `tests/test_workflows.py` – full card order lifecycle, idempotent checkout, duplicate payment + webhook protection, cancellation with refund + stock release, failed payment, COD, transfers, negative stock prevention, audit log immutability, role-based dashboard, CSV/Excel/PDF exports, tickets, suppliers → PO → invoice

---

## Payments

By default the **sandbox gateway** is used – no keys needed. It behaves like a real gateway: creates payment intents, signs webhooks with HMAC-SHA256, and you trigger success/failure with `/payments/sandbox/{ref}/simulate`.

To use **Stripe test mode**, put your keys in `.env`:

```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

Point the Stripe webhook at `POST /payments/webhook`. Webhook signatures are verified either way.

**Duplicate protection:** one pending payment per order (repeat calls return it), `Idempotency-Key` on checkout and payments, webhook events stored by event id (replays are ignored), row locks (`SELECT … FOR UPDATE`) on orders, payments and stock.

---

## Project structure

```
app/
  main.py            app, routers, background scheduler
  config.py          settings from .env
  database.py        engine + session
  security.py        bcrypt + JWT
  deps.py            current user, require_roles(), ownership checks
  roles.py           the 9 roles
  models/            SQLAlchemy tables (users, catalog, inventory, sales, payments, logistics, ...)
  schemas/           Pydantic request/response models
  routers/           endpoints (one file per module group)
  services/          business logic: pricing, stock, orders, gateway, notify, audit, reports, jobs
alembic/             migrations
tests/               pytest
postman/             Postman collection
create_db.py         creates the MySQL database
seed.py              sample data
setup.ps1 run.ps1 test.ps1 reset-db.ps1
```

## Where each module lives

| Modules | File |
|---|---|
| 1 Auth, 3 Registration | `routers/auth.py` |
| 2 User management | `routers/users.py` |
| 4 Profile, 5 Addresses | `routers/customers.py` |
| 6 Categories, 7 Brands, 11 Attributes | `routers/catalog.py` |
| 8 Products, 9 Variants, 10 Files, 12 Pricing | `routers/products.py` |
| 13 Inventory, 14 Warehouses, 15 Transfers, 16 Low stock | `routers/inventory.py` |
| 17 Cart, 18 Cart pricing, 19 Wishlist | `routers/cart.py` + `services/pricing.py` |
| 20 Coupons, 21 Promotions, 22 Tax, 23 Shipping config | `routers/marketing.py` |
| 24 Checkout, 25 Orders, 26 Order items, 27 Status, 28 Cancellation | `routers/orders.py` + `services/orders.py` |
| 29 Payments, 30 History, 31 Refunds, 32 COD | `routers/payments.py` + `services/gateway.py` |
| 33 Shipments, 34 Tracking, 35 Delivery | `routers/logistics.py` |
| 36 Returns, 37 Exchanges | `routers/returns.py` |
| 38 Reviews, 39 Q&A | `routers/engagement.py` |
| 40 Support tickets | `routers/support.py` |
| 41 Notifications, 42 Email/SMS | `routers/notifications.py` + `services/notify.py` |
| 43 Suppliers, 44 Purchase orders, 45 Invoices | `routers/suppliers.py` |
| 46 Audit, 47 Dashboard, 48 Reports, 49 Exports/jobs | `routers/admin.py` + `services/reports.py`, `services/jobs.py` |
| 50 Testing | `tests/`, `postman/` |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `running scripts is disabled on this system` | Use `powershell -ExecutionPolicy Bypass -File .\setup.ps1` |
| `Wrong username or password` | Edit `DB_USER` / `DB_PASSWORD` in `.env` (or delete `.env` and rerun setup) |
| `MySQL server is not running` | Win + R → `services.msc` → **MySQL80** → Start |
| `python is not recognized` | Reinstall Python and tick **Add python.exe to PATH** |
| Port 8000 already in use | Edit `run.ps1` and change `--port 8000` to `--port 8001` |
| Password has `@` or `#` | Works fine – the URL is escaped for you |
| Emails don't arrive | By default they print in the terminal (`EMAIL_PROVIDER=console`). Set SMTP values in `.env` for real email |
