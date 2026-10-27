# Module 6: categories, Module 7: brands
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Brand, Category, Product, User
from app.roles import ADMIN, PRODUCT_MANAGER
from app.schemas.catalog import (ActiveIn, BrandIn, BrandOut, CategoryIn, CategoryOut, CategoryTree,
                                 CategoryUpdate, ProductOut)
from app.schemas.common import Page
from app.services.audit import log_action
from app.utils import get_or_404, paginate

router = APIRouter(tags=["6. Categories, 7. Brands"])
catalog_staff = require_roles(ADMIN, PRODUCT_MANAGER)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---------------- categories ----------------
@router.get("/categories", response_model=list[CategoryOut])
def list_categories(include_inactive: bool = False, db: Session = Depends(get_db)):
    q = db.query(Category)
    if not include_inactive:
        q = q.filter(Category.is_active.is_(True))
    return q.order_by(Category.name).all()


@router.get("/categories/tree", response_model=list[CategoryTree])
def category_tree(db: Session = Depends(get_db)):
    cats = db.query(Category).filter(Category.is_active.is_(True)).order_by(Category.name).all()
    nodes = {c.id: {"id": c.id, "name": c.name, "slug": c.slug, "is_active": c.is_active, "children": []} for c in cats}
    roots = []
    for c in cats:
        if c.parent_id and c.parent_id in nodes:
            nodes[c.parent_id]["children"].append(nodes[c.id])
        else:
            roots.append(nodes[c.id])
    return roots


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    slug = data.slug or slugify(data.name)
    if db.query(Category).filter_by(slug=slug).first():
        raise HTTPException(409, "Category with this slug already exists")
    if data.parent_id:
        get_or_404(db, Category, data.parent_id, "Parent category")
    cat = Category(name=data.name, slug=slug, description=data.description,
                   parent_id=data.parent_id, is_active=data.is_active)
    db.add(cat)
    db.flush()
    log_action(db, me.id, "category.create", "category", cat.id, None, {"name": cat.name})
    db.commit()
    return cat


@router.patch("/categories/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db),
                    me: User = Depends(catalog_staff)):
    cat = get_or_404(db, Category, cat_id, "Category")
    changes = data.model_dump(exclude_unset=True)
    if "parent_id" in changes and changes["parent_id"]:
        # walk up the tree to make sure we don't create a loop
        parent = get_or_404(db, Category, changes["parent_id"], "Parent category")
        while parent:
            if parent.id == cat.id:
                raise HTTPException(400, "Category can't be its own parent / child")
            parent = db.get(Category, parent.parent_id) if parent.parent_id else None
    for k, v in changes.items():
        setattr(cat, k, v)
    db.commit()
    return cat


@router.put("/categories/{cat_id}/status", response_model=CategoryOut)
def category_status(cat_id: int, data: ActiveIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    cat = get_or_404(db, Category, cat_id, "Category")
    cat.is_active = data.is_active
    log_action(db, me.id, "category.status", "category", cat.id, None, {"is_active": data.is_active})
    db.commit()
    return cat


@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    cat = get_or_404(db, Category, cat_id, "Category")
    if db.query(Category).filter_by(parent_id=cat.id).count():
        raise HTTPException(400, "Category has subcategories, move or delete them first")
    if db.query(Product).filter_by(category_id=cat.id).count():
        raise HTTPException(400, "Category has products, deactivate it instead")
    log_action(db, me.id, "category.delete", "category", cat.id, {"name": cat.name}, None)
    db.delete(cat)
    db.commit()


# ---------------- brands ----------------
@router.get("/brands", response_model=Page[BrandOut])
def list_brands(search: Optional[str] = None, active: Optional[bool] = None, page: int = 1, size: int = 20,
                db: Session = Depends(get_db)):
    q = db.query(Brand)
    if search:
        q = q.filter(Brand.name.ilike(f"%{search}%"))
    if active is not None:
        q = q.filter(Brand.is_active.is_(active))
    return paginate(q.order_by(Brand.name), page, size)


@router.post("/brands", response_model=BrandOut, status_code=201)
def create_brand(data: BrandIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    if db.query(Brand).filter(Brand.name == data.name).first():
        raise HTTPException(409, "Brand already exists")
    brand = Brand(**data.model_dump())
    db.add(brand)
    db.commit()
    return brand


@router.put("/brands/{brand_id}", response_model=BrandOut)
def update_brand(brand_id: int, data: BrandIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    brand = get_or_404(db, Brand, brand_id, "Brand")
    if db.query(Brand).filter(Brand.name == data.name, Brand.id != brand_id).first():
        raise HTTPException(409, "Brand name taken")
    for k, v in data.model_dump().items():
        setattr(brand, k, v)
    db.commit()
    return brand


@router.put("/brands/{brand_id}/status", response_model=BrandOut)
def brand_status(brand_id: int, data: ActiveIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    brand = get_or_404(db, Brand, brand_id, "Brand")
    brand.is_active = data.is_active
    db.commit()
    return brand


@router.get("/brands/{brand_id}/products", response_model=Page[ProductOut])
def products_by_brand(brand_id: int, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    get_or_404(db, Brand, brand_id, "Brand")
    q = db.query(Product).filter(Product.brand_id == brand_id, Product.is_active.is_(True))
    return paginate(q.order_by(Product.name), page, size)