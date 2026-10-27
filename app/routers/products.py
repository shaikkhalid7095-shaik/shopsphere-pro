# Module 8 products, Module 9 variants, Module 10 images & documents
import os
import uuid
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import require_roles
from app.models import (Attribute, Brand, Category, PriceHistory, Product, ProductAttributeValue, ProductFile,
                        ProductVariant, Review, Supplier, User)
from app.roles import ADMIN, PRODUCT_MANAGER
from app.schemas.catalog import (ActiveIn, FileOut, ProductDetail, ProductIn, ProductOut, ProductUpdate,
                                 VariantIn, VariantOut, VariantUpdate)
from app.schemas.common import Page
from app.services.audit import log_action
from app.services.pricing import effective_price
from app.services.stock import total_available
from app.utils import get_or_404, paginate

router = APIRouter(prefix="/products", tags=["8. Products, 9. Variants, 10. Files"])
catalog_staff = require_roles(ADMIN, PRODUCT_MANAGER)

IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
DOC_TYPES = {"application/pdf": ".pdf", "text/plain": ".txt"}
MAX_IMAGE = 5 * 1024 * 1024
MAX_DOC = 10 * 1024 * 1024


def _child_category_ids(db, cat_id):
    ids, todo = [cat_id], [cat_id]
    while todo:
        kids = [c.id for c in db.query(Category.id).filter(Category.parent_id.in_(todo)).all()]
        ids += kids
        todo = kids
    return ids


def _check_refs(db, data):
    cat = db.get(Category, data.get("category_id")) if data.get("category_id") else None
    if data.get("category_id") and (not cat or not cat.is_active):
        raise HTTPException(400, "Category not found or inactive")
    if data.get("brand_id"):
        brand = db.get(Brand, data["brand_id"])
        if not brand or not brand.is_active:
            raise HTTPException(400, "Brand not found or inactive")
    if data.get("seller_id"):
        seller = db.get(Supplier, data["seller_id"])
        if not seller or seller.status != "approved":
            raise HTTPException(400, "Seller not found or not approved")


# ---------------- products ----------------
@router.get("", response_model=Page[ProductOut])
def search_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    attr: List[str] = Query(default=[], description="filter like attr=Color:Red (repeatable)"),
    include_inactive: bool = False,
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc|name)$"),
    page: int = 1, size: int = 20,
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if not include_inactive:
        q = q.filter(Product.is_active.is_(True))
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Product.name.ilike(like), Product.sku.ilike(like), Product.description.ilike(like)))
    if category_id:
        q = q.filter(Product.category_id.in_(_child_category_ids(db, category_id)))
    if brand_id:
        q = q.filter(Product.brand_id == brand_id)
    price_col = func.coalesce(Product.sale_price, Product.base_price)
    if min_price is not None:
        q = q.filter(price_col >= min_price)
    if max_price is not None:
        q = q.filter(price_col <= max_price)
    for a in attr:
        if ":" not in a:
            raise HTTPException(400, "attr filter must look like Name:Value")
        name, value = a.split(":", 1)
        sub = db.query(ProductAttributeValue.product_id).join(Attribute).filter(
            Attribute.name == name, ProductAttributeValue.value == value)
        q = q.filter(Product.id.in_(sub))

    order = {"newest": Product.id.desc(), "price_asc": price_col.asc(),
             "price_desc": price_col.desc(), "name": Product.name.asc()}[sort]
    return paginate(q.order_by(order), page, size)


@router.post("", response_model=ProductOut, status_code=201)
def create_product(data: ProductIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    if db.query(Product).filter_by(sku=data.sku).first() or db.query(ProductVariant).filter_by(sku=data.sku).first():
        raise HTTPException(409, "SKU already exists")
    _check_refs(db, data.model_dump())
    product = Product(**data.model_dump())
    db.add(product)
    db.flush()
    db.add(PriceHistory(product_id=product.id, new_base=product.base_price, new_sale=product.sale_price,
                        changed_by=me.id))
    log_action(db, me.id, "product.create", "product", product.id, None,
               {"sku": product.sku, "price": product.base_price})
    db.commit()
    return product


@router.get("/{product_id}", response_model=ProductDetail)
def product_detail(product_id: int, db: Session = Depends(get_db)):
    p = get_or_404(db, Product, product_id, "Product")
    variants = []
    for v in p.variants:
        out = VariantOut.model_validate(v)
        out.available = total_available(db, p.id, v.id)
        variants.append(out)
    attrs = db.query(ProductAttributeValue).filter_by(product_id=p.id).all()
    files = db.query(ProductFile).filter_by(product_id=p.id).all()
    avg, cnt = db.query(func.avg(Review.rating), func.count(Review.id)).filter(
        Review.product_id == p.id, Review.status == "published").one()
    base = ProductOut.model_validate(p).model_dump()
    return ProductDetail(
        **base,
        current_price=effective_price(p),
        category_name=p.category.name if p.category else None,
        brand_name=p.brand.name if p.brand else None,
        available=total_available(db, p.id, None),
        variants=variants,
        attributes=[{"attribute_id": a.attribute_id, "name": a.attribute.name, "value": a.value} for a in attrs],
        files=[FileOut.model_validate(f) for f in files],
        rating_avg=round(float(avg), 2) if avg else None,
        rating_count=cnt,
    )


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db),
                   me: User = Depends(catalog_staff)):
    p = get_or_404(db, Product, product_id, "Product")
    changes = data.model_dump(exclude_unset=True)
    _check_refs(db, changes)
    old = {k: getattr(p, k) for k in changes}
    for k, v in changes.items():
        setattr(p, k, v)
    log_action(db, me.id, "product.update", "product", p.id, old, changes)
    db.commit()
    return p


@router.put("/{product_id}/status", response_model=ProductOut)
def product_status(product_id: int, data: ActiveIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    p = get_or_404(db, Product, product_id, "Product")
    p.is_active = data.is_active
    log_action(db, me.id, "product.status", "product", p.id, None, {"is_active": data.is_active})
    db.commit()
    return p


@router.delete("/{product_id}", response_model=ProductOut)
def deactivate_product(product_id: int, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    return product_status(product_id, ActiveIn(is_active=False), db, me)


# ---------------- variants ----------------
@router.get("/{product_id}/variants", response_model=list[VariantOut])
def list_variants(product_id: int, db: Session = Depends(get_db)):
    p = get_or_404(db, Product, product_id, "Product")
    out = []
    for v in p.variants:
        item = VariantOut.model_validate(v)
        item.available = total_available(db, p.id, v.id)
        out.append(item)
    return out


@router.post("/{product_id}/variants", response_model=VariantOut, status_code=201)
def add_variant(product_id: int, data: VariantIn, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    get_or_404(db, Product, product_id, "Product")
    if db.query(ProductVariant).filter_by(sku=data.sku).first() or db.query(Product).filter_by(sku=data.sku).first():
        raise HTTPException(409, "SKU already exists")
    dup = db.query(ProductVariant).filter_by(product_id=product_id, size=data.size, color=data.color).first()
    if dup:
        raise HTTPException(409, "A variant with this size/color already exists")
    v = ProductVariant(product_id=product_id, **data.model_dump())
    db.add(v)
    db.commit()
    return v


@router.patch("/variants/{variant_id}", response_model=VariantOut)
def update_variant(variant_id: int, data: VariantUpdate, db: Session = Depends(get_db),
                   me: User = Depends(catalog_staff)):
    v = get_or_404(db, ProductVariant, variant_id, "Variant")
    changes = data.model_dump(exclude_unset=True)
    if "price" in changes and changes["price"] != v.price:
        db.add(PriceHistory(product_id=v.product_id, variant_id=v.id, old_base=v.price,
                            new_base=changes["price"], changed_by=me.id))
        log_action(db, me.id, "variant.price_change", "variant", v.id, {"price": v.price}, {"price": changes["price"]})
    for k, val in changes.items():
        setattr(v, k, val)
    db.commit()
    return v


# ---------------- files ----------------
@router.post("/{product_id}/files", response_model=FileOut, status_code=201)
async def upload_file(product_id: int, file: UploadFile = File(...), variant_id: Optional[int] = Form(None),
                      db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    get_or_404(db, Product, product_id, "Product")
    if variant_id:
        v = db.get(ProductVariant, variant_id)
        if not v or v.product_id != product_id:
            raise HTTPException(400, "Variant does not belong to this product")

    if file.content_type in IMAGE_TYPES:
        kind, ext, limit = "image", IMAGE_TYPES[file.content_type], MAX_IMAGE
    elif file.content_type in DOC_TYPES:
        kind, ext, limit = "document", DOC_TYPES[file.content_type], MAX_DOC
    else:
        raise HTTPException(400, "Only JPG, PNG, WEBP images or PDF/TXT documents allowed")

    content = await file.read()
    if len(content) > limit:
        raise HTTPException(400, f"File too large, max {limit // (1024 * 1024)} MB")
    if not content:
        raise HTTPException(400, "Empty file")

    os.makedirs(settings.upload_dir, exist_ok=True)
    stored = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(settings.upload_dir, stored), "wb") as fh:
        fh.write(content)

    row = ProductFile(product_id=product_id, variant_id=variant_id, file_kind=kind,
                      original_name=file.filename, stored_name=stored, content_type=file.content_type,
                      size_bytes=len(content), uploaded_by=me.id)
    db.add(row)
    db.commit()
    return row


@router.get("/{product_id}/files", response_model=list[FileOut])
def list_files(product_id: int, db: Session = Depends(get_db)):
    return db.query(ProductFile).filter_by(product_id=product_id).all()


@router.get("/files/{file_id}/download")
def download_file(file_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, ProductFile, file_id, "File")
    path = os.path.join(settings.upload_dir, row.stored_name)
    if not os.path.exists(path):
        raise HTTPException(404, "File missing on disk")
    return FileResponse(path, media_type=row.content_type, filename=row.original_name)


@router.delete("/files/{file_id}", status_code=204)
def delete_file(file_id: int, db: Session = Depends(get_db), me: User = Depends(catalog_staff)):
    row = get_or_404(db, ProductFile, file_id, "File")
    path = os.path.join(settings.upload_dir, row.stored_name)
    if os.path.exists(path):
        os.remove(path)
    db.delete(row)
    db.commit()