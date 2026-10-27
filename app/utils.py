import random
import string
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException


def now():
    # naive utc - mysql DATETIME has no timezone
    return datetime.now(timezone.utc).replace(tzinfo=None)


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def make_code(prefix: str, length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    stamp = now().strftime("%y%m%d")
    return f"{prefix}-{stamp}-{''.join(random.choices(chars, k=length))}"


def get_or_404(db, model, obj_id, name=None):
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(404, f"{name or model.__name__} not found")
    return obj


def paginate(query, page: int = 1, size: int = 20):
    size = max(1, min(size, 100))
    page = max(1, page)
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {"total": total, "page": page, "size": size, "items": items}