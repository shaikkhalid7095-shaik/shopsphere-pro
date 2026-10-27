"""
Fills the database with roles, staff accounts and sample shop data.
Safe to run more than once - it skips things that already exist.
Run:  python seed.py
"""
from datetime import timedelta
from decimal import Decimal

from app.database import SessionLocal
from app.models import (Address, Attribute, Brand, Category, CodSetting, Coupon, Inventory, Permission, Product,
                        ProductAttributeValue, ProductVariant, Promotion, Role, ShippingMethod, ShippingProvider,
                        Supplier, TaxRate, User, Warehouse)
from app.roles import ALL_ROLES, ROLE_PERMISSIONS
from app.security import hash_password
from app.utils import now

PASSWORD = "Password@123"

STAFF = [
    ("superadmin@shopsphere.com", "Super Admin", "super_admin", "9000000001"),
    ("admin@shopsphere.com", "Asha Admin", "admin", "9000000002"),
    ("products@shopsphere.com", "Pranav Products", "product_manager", "9000000003"),
    ("inventory@shopsphere.com", "Imran Inventory", "inventory_manager", "9000000004"),
    ("orders@shopsphere.com", "Olivia Orders", "order_manager", "9000000005"),
    ("support@shopsphere.com", "Sana Support", "support_agent", "9000000006"),
    ("delivery@shopsphere.com", "Dev Delivery", "delivery_manager", "9000000007"),
    ("finance@shopsphere.com", "Farhan Finance", "finance_manager", "9000000008"),
    ("customer@shopsphere.com", "Ravi Customer", "customer", "9876543210"),
    ("customer2@shopsphere.com", "Meena Customer", "customer", "9876543211"),
]


def get_or_create(db, model, lookup, **extra):
    obj = db.query(model).filter_by(**lookup).first()
    if obj:
        return obj, False
    obj = model(**lookup, **extra)
    db.add(obj)
    db.flush()
    return obj, True


def run():
    db = SessionLocal()
    try:
        # roles + permissions
        for name in ALL_ROLES:
            role, _ = get_or_create(db, Role, {"name": name}, description=name.replace("_", " ").title())
            if not role.permissions:
                for code in ROLE_PERMISSIONS.get(name, []):
                    perm, _ = get_or_create(db, Permission, {"code": code})
                    role.permissions.append(perm)
        db.flush()

        users = {}
        for email, name, role_name, phone in STAFF:
            role = db.query(Role).filter_by(name=role_name).first()
            user, _ = get_or_create(db, User, {"email": email}, full_name=name, phone=phone,
                                    password_hash=hash_password(PASSWORD), role_id=role.id,
                                    is_email_verified=True, registration_status="completed")
            users[email] = user

        # catalog
        electronics, _ = get_or_create(db, Category, {"slug": "electronics"}, name="Electronics")
        phones, _ = get_or_create(db, Category, {"slug": "mobiles"}, name="Mobiles", parent_id=electronics.id)
        fashion, _ = get_or_create(db, Category, {"slug": "fashion"}, name="Fashion")
        tshirts, _ = get_or_create(db, Category, {"slug": "t-shirts"}, name="T-Shirts", parent_id=fashion.id)

        samsung, _ = get_or_create(db, Brand, {"name": "Samsung"})
        boat, _ = get_or_create(db, Brand, {"name": "boAt"})
        urban, _ = get_or_create(db, Brand, {"name": "UrbanWear"})

        main_wh, _ = get_or_create(db, Warehouse, {"code": "HYD01"}, name="Hyderabad Main", city="Hyderabad",
                                   capacity=50000)
        blr_wh, _ = get_or_create(db, Warehouse, {"code": "BLR01"}, name="Bengaluru Hub", city="Bengaluru",
                                  capacity=20000)

        seller, _ = get_or_create(db, Supplier, {"email": "sales@techdistributors.in"}, name="Tech Distributors",
                                  kind="supplier", contact_name="Kiran", phone="9123456780",
                                  gst_number="36ABCDE1234F1Z5", status="approved")

        phone_p, made_phone = get_or_create(
            db, Product, {"sku": "SAM-M14"}, name="Samsung Galaxy M14", category_id=phones.id,
            brand_id=samsung.id, base_price=Decimal("14999"), sale_price=Decimal("12999"),
            description="6000mAh battery, 50MP camera")
        earbuds, _ = get_or_create(
            db, Product, {"sku": "BOAT-AIR141"}, name="boAt Airdopes 141", category_id=electronics.id,
            brand_id=boat.id, base_price=Decimal("1499"), description="42h playback, ENx tech")
        tshirt, made_tee = get_or_create(
            db, Product, {"sku": "UW-TEE-BASIC"}, name="Basic Cotton T-Shirt", category_id=tshirts.id,
            brand_id=urban.id, base_price=Decimal("599"), description="100% cotton regular fit")

        variants = []
        if made_tee:
            for size, color in [("M", "Black"), ("L", "Black"), ("M", "White")]:
                v = ProductVariant(product_id=tshirt.id, sku=f"UW-TEE-{color[:3].upper()}-{size}", size=size,
                                   color=color)
                db.add(v)
                variants.append(v)
            db.flush()

        # attributes
        color_attr, _ = get_or_create(db, Attribute, {"name": "Color"}, data_type="choice",
                                      allowed_values="Black,White,Blue,Red")
        ram_attr, _ = get_or_create(db, Attribute, {"name": "RAM (GB)"}, data_type="number", category_id=phones.id)
        if made_phone:
            db.add(ProductAttributeValue(product_id=phone_p.id, attribute_id=ram_attr.id, value="6"))
            db.add(ProductAttributeValue(product_id=phone_p.id, attribute_id=color_attr.id, value="Blue"))

        # stock
        def stock(product_id, variant_id, wh, qty):
            q = db.query(Inventory).filter_by(product_id=product_id, warehouse_id=wh.id)
            q = q.filter(Inventory.variant_id == variant_id) if variant_id else q.filter(Inventory.variant_id.is_(None))
            if not q.first():
                db.add(Inventory(product_id=product_id, variant_id=variant_id, warehouse_id=wh.id, quantity=qty,
                                 reserved=0, min_threshold=5))

        stock(phone_p.id, None, main_wh, 50)
        stock(phone_p.id, None, blr_wh, 20)
        stock(earbuds.id, None, main_wh, 100)
        for v in variants:
            stock(tshirt.id, v.id, main_wh, 40)

        # pricing rules
        get_or_create(db, TaxRate, {"name": "GST 18%", "category_id": electronics.id}, rate=Decimal("18"))
        get_or_create(db, TaxRate, {"name": "GST 18% Mobiles", "category_id": phones.id}, rate=Decimal("18"))
        get_or_create(db, TaxRate, {"name": "GST 5% Apparel", "category_id": tshirts.id}, rate=Decimal("5"))
        get_or_create(db, ShippingMethod, {"code": "STANDARD"}, name="Standard Delivery", base_charge=Decimal("49"),
                      per_item_charge=Decimal("0"), free_above=Decimal("999"), min_days=3, max_days=6,
                      allowed_countries="India")
        get_or_create(db, ShippingMethod, {"code": "EXPRESS"}, name="Express Delivery", base_charge=Decimal("149"),
                      per_item_charge=Decimal("20"), min_days=1, max_days=2, allowed_countries="India", max_items=10)
        get_or_create(db, Coupon, {"code": "WELCOME10"}, description="10% off up to 500", discount_type="percent",
                      value=Decimal("10"), max_discount=Decimal("500"), min_purchase=Decimal("499"),
                      valid_from=now() - timedelta(days=1), valid_to=now() + timedelta(days=90))
        get_or_create(db, Coupon, {"code": "FLAT100"}, description="Flat 100 off", discount_type="fixed",
                      value=Decimal("100"), min_purchase=Decimal("999"), usage_limit=100)
        get_or_create(db, Promotion, {"name": "T-Shirt Fest"}, scope="category", category_id=tshirts.id,
                      discount_type="percent", value=Decimal("10"), min_quantity=2,
                      start_at=now() - timedelta(days=1), end_at=now() + timedelta(days=30))
        if not db.query(CodSetting).first():
            db.add(CodSetting(is_enabled=True, max_order_amount=Decimal("20000"), allowed_countries="India"))

        get_or_create(db, ShippingProvider, {"code": "DELHIVERY"}, name="Delhivery",
                      tracking_url="https://www.delhivery.com/track/package/{tracking}")
        get_or_create(db, ShippingProvider, {"code": "BLUEDART"}, name="Blue Dart")

        # an address for the demo customer
        cust = users["customer@shopsphere.com"]
        if not db.query(Address).filter_by(user_id=cust.id).first():
            db.add(Address(user_id=cust.id, label="Home", address_type="shipping", full_name=cust.full_name,
                           phone=cust.phone, line1="Plot 12, Road No 3", line2="Banjara Hills", city="Hyderabad",
                           state="Telangana", postal_code="500034", country="India", is_default=True))

        db.commit()
        print("[OK] Seed data loaded")
        print(f"     All sample accounts use password: {PASSWORD}")
        for email, _, role_name, _ in STAFF:
            print(f"     {role_name:<18} {email}")
    finally:
        db.close()


if __name__ == "__main__":
    run()