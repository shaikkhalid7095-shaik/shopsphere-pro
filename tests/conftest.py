import os

# tests run on a throwaway sqlite file so they never touch your MySQL data.
# to run them on a separate MySQL test database set TEST_DATABASE_URL, e.g.
#   mysql+pymysql://root:pass@localhost/shopsphere_test
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite:///./test_shopsphere.db")
os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["DEBUG"] = "true"
os.environ["STRIPE_SECRET_KEY"] = ""
os.environ["EXPORT_DIR"] = "test_exports"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
import app.models  # noqa: E402,F401
from app.main import app as fastapi_app  # noqa: E402
import seed  # noqa: E402

PASSWORD = "Password@123"


@pytest.fixture(scope="session", autouse=True)
def database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed.run()
    yield
    engine.dispose()
    if os.path.exists("test_shopsphere.db"):
        os.remove("test_shopsphere.db")


@pytest.fixture(scope="session")
def client():
    with TestClient(fastapi_app) as c:
        yield c


_token_cache = {}


def login(client, email, password=PASSWORD):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def auth(client):
    def _get(role):
        emails = {
            "super_admin": "superadmin@shopsphere.com", "admin": "admin@shopsphere.com",
            "product_manager": "products@shopsphere.com", "inventory_manager": "inventory@shopsphere.com",
            "order_manager": "orders@shopsphere.com", "support_agent": "support@shopsphere.com",
            "delivery_manager": "delivery@shopsphere.com", "finance_manager": "finance@shopsphere.com",
            "customer": "customer@shopsphere.com", "customer2": "customer2@shopsphere.com",
        }
        if role not in _token_cache:
            _token_cache[role] = login(client, emails[role])
        return _token_cache[role]
    return _get