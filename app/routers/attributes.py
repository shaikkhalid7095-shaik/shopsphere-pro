# Module 11: product attributes (size, material, color ...)
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Attribute, Category, Product, ProductAttributeValue, User
from app.roles import ADMIN, PRODUCT_MANAGER
from app.schemas.catalog import AssignAttributeIn, AttributeIn, AttributeOut
from app.utils import get_or_404

router = APIRouter(tags=["11. Attributes"])
catalog_staff = require_roles(ADMIN, PRODUCT_MANAGER)


# ---------------- attributes ----------------
@router.get("/attributes", response_model=list[AttributeOut])
def list_attributes(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Attribute)
    if category_id:
        q = q.filter((Attribute.category_id == category_id) | (Attribute.category_id.is_(None)))
    return q.order_by(Attribute.name).all()


@router.post("/attributes", response_model=AttributeOut, status_code=201)
def create_attribute(data: AttributeIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    if db.query(Attribute).filter_by(name=data.name).first():
        raise HTTPException(409, "Attribute exists")
    if data.category_id:
        get_or_404(db, Category, data.category_id, "Category")
    attr = Attribute(name=data.name, data_type=data.data_type, category_id=data.category_id,
                     allowed_values=",".join(v.strip() for v in data.allowed_values) if data.allowed_values else None)
    db.add(attr)
    db.commit()
    return attr


def validate_attr_value(attr: Attribute, value: str):
    if attr.data_type == "number":
        try:
            float(value)
        except ValueError:
            raise HTTPException(400, f"{attr.name} must be a number")
    if attr.data_type == "choice":
        allowed = [v.strip().lower() for v in (attr.allowed_values or "").split(",")]
        if value.strip().lower() not in allowed:
            raise HTTPException(400, f"{attr.name} must be one of: {attr.allowed_values}")


@router.put("/products/{product_id}/attributes")
def assign_attribute(product_id: int, data: AssignAttributeIn, db: Session = Depends(get_db),
                     me: User = Depends(catalog_staff)):
    product = get_or_404(db, Product, product_id, "Product")
    attr = get_or_404(db, Attribute, data.attribute_id, "Attribute")
    if attr.category_id and attr.category_id != product.category_id:
        raise HTTPException(400, f"Attribute '{attr.name}' is not allowed for this product's category")
    validate_attr_value(attr, data.value)
    row = db.query(ProductAttributeValue).filter_by(product_id=product_id, attribute_id=attr.id).first()
    if row:
        row.value = data.value
    else:
        db.add(ProductAttributeValue(product_id=product_id, attribute_id=attr.id, value=data.value))
    db.commit()
    return {"product_id": product_id, "attribute": attr.name, "value": data.value}


@router.delete("/products/{product_id}/attributes/{attribute_id}", status_code=204)
def remove_attribute(product_id: int, attribute_id: int, db: Session = Depends(get_db),
                     me: User = Depends(catalog_staff)):
    row = db.query(ProductAttributeValue).filter_by(product_id=product_id, attribute_id=attribute_id).first()
    if not row:
        raise HTTPException(404, "Attribute not assigned")
    db.delete(row)
    db.commit()