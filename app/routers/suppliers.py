# Module 43 sellers/suppliers, 44 purchase orders, 45 supplier invoices
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import (ConfigHistory, Product, ProductVariant, PurchaseOrder, PurchaseOrderItem, Supplier,
                        SupplierInvoice, SupplierProduct, User, Warehouse)
from app.roles import ADMIN, FINANCE_MANAGER, INVENTORY_MANAGER, PRODUCT_MANAGER
from app.schemas.common import Page
from app.schemas.sales import HistoryOut
from app.schemas.suppliers import (InvoiceIn, InvoiceOut, InvoicePayIn, LinkProductIn, POIn, POOut, POReceiveIn,
                                   SupplierIn, SupplierOut, SupplierStatusIn)
from app.services import stock
from app.services.audit import log_action, row_to_dict, save_history
from app.utils import get_or_404, make_code, money, paginate

router = APIRouter(tags=["43. Suppliers, 44. Purchase Orders, 45. Invoices"])
supplier_staff = require_roles(ADMIN, INVENTORY_MANAGER, PRODUCT_MANAGER)
po_staff = require_roles(ADMIN, INVENTORY_MANAGER)
finance = require_roles(ADMIN, FINANCE_MANAGER)


# ---------------- suppliers ----------------
@router.post("/suppliers", response_model=SupplierOut, status_code=201)
def register_supplier(data: SupplierIn, db: Session = Depends(get_db), me: User = Depends(supplier_staff)):
    if db.query(Supplier).filter_by(email=data.email.lower()).first():
        raise HTTPException(409, "Supplier with this email exists")
    s = Supplier(**data.model_dump())
    s.email = s.email.lower()
    db.add(s)
    db.flush()
    save_history(db, "supplier", s.id, "registered", data.model_dump(), me.id)
    db.commit()
    return s


@router.get("/suppliers", response_model=Page[SupplierOut])
def list_suppliers(search: Optional[str] = None, status: Optional[str] = None, kind: Optional[str] = None,
                   page: int = 1, size: int = 20, db: Session = Depends(get_db), _=Depends(supplier_staff)):
    q = db.query(Supplier)
    if search:
        q = q.filter(or_(Supplier.name.ilike(f"%{search}%"), Supplier.email.ilike(f"%{search}%")))
    if status:
        q = q.filter_by(status=status)
    if kind:
        q = q.filter_by(kind=kind)
    return paginate(q.order_by(Supplier.name), page, size)


@router.get("/suppliers/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db), _=Depends(supplier_staff)):
    return get_or_404(db, Supplier, supplier_id, "Supplier")


@router.put("/suppliers/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, data: SupplierIn, db: Session = Depends(get_db),
                    me: User = Depends(supplier_staff)):
    s = get_or_404(db, Supplier, supplier_id, "Supplier")
    old = row_to_dict(s)
    for k, v in data.model_dump().items():
        setattr(s, k, v)
    save_history(db, "supplier", s.id, "updated", {"old": old, "new": data.model_dump()}, me.id)
    db.commit()
    return s


@router.put("/suppliers/{supplier_id}/status", response_model=SupplierOut)
def supplier_status(supplier_id: int, data: SupplierStatusIn, db: Session = Depends(get_db),
                    me: User = Depends(require_roles(ADMIN))):
    s = get_or_404(db, Supplier, supplier_id, "Supplier")
    old = s.status
    s.status = data.status
    save_history(db, "supplier", s.id, f"status:{data.status}", {"from": old, "note": data.note}, me.id)
    log_action(db, me.id, "supplier.status", "supplier", s.id, {"status": old}, {"status": data.status})
    db.commit()
    return s


@router.get("/suppliers/{supplier_id}/history", response_model=list[HistoryOut])
def supplier_history(supplier_id: int, db: Session = Depends(get_db), _=Depends(supplier_staff)):
    return db.query(ConfigHistory).filter_by(entity="supplier", entity_id=supplier_id).order_by(ConfigHistory.id).all()


@router.post("/suppliers/{supplier_id}/products")
def link_product(supplier_id: int, data: LinkProductIn, db: Session = Depends(get_db),
                 me: User = Depends(supplier_staff)):
    s = get_or_404(db, Supplier, supplier_id, "Supplier")
    if s.status != "approved":
        raise HTTPException(400, "Supplier must be approved first")
    product = get_or_404(db, Product, data.product_id, "Product")
    link = db.query(SupplierProduct).filter_by(supplier_id=s.id, product_id=product.id).first()
    if link:
        link.cost_price = data.cost_price
    else:
        db.add(SupplierProduct(supplier_id=s.id, product_id=product.id, cost_price=data.cost_price))
    if s.kind == "seller":
        product.seller_id = s.id  # marketplace seller owns the listing
    db.commit()
    return {"supplier_id": s.id, "product_id": product.id, "cost_price": data.cost_price}


@router.get("/suppliers/{supplier_id}/products")
def supplier_products(supplier_id: int, db: Session = Depends(get_db), _=Depends(supplier_staff)):
    rows = db.query(SupplierProduct, Product).join(Product, Product.id == SupplierProduct.product_id) \
             .filter(SupplierProduct.supplier_id == supplier_id).all()
    return [{"product_id": p.id, "name": p.name, "sku": p.sku, "cost_price": sp.cost_price} for sp, p in rows]


# ---------------- purchase orders ----------------
@router.post("/purchase-orders", response_model=POOut, status_code=201)
def create_po(data: POIn, db: Session = Depends(get_db), me: User = Depends(po_staff)):
    s = get_or_404(db, Supplier, data.supplier_id, "Supplier")
    if s.status != "approved":
        raise HTTPException(400, "Supplier is not approved")
    get_or_404(db, Warehouse, data.warehouse_id, "Warehouse")
    po = PurchaseOrder(po_number=make_code("PO"), supplier_id=s.id, warehouse_id=data.warehouse_id,
                       expected_date=data.expected_date, created_by=me.id)
    total = Decimal("0")
    for it in data.items:
        get_or_404(db, Product, it.product_id, "Product")
        if it.variant_id:
            v = db.get(ProductVariant, it.variant_id)
            if not v or v.product_id != it.product_id:
                raise HTTPException(400, "Variant does not match product")
        po.items.append(PurchaseOrderItem(**it.model_dump()))
        total += Decimal(it.unit_cost) * it.quantity
    po.total_amount = money(total)
    db.add(po)
    db.commit()
    return po


@router.get("/purchase-orders", response_model=Page[POOut])
def list_pos(supplier_id: Optional[int] = None, status: Optional[str] = None, page: int = 1, size: int = 20,
             db: Session = Depends(get_db), _=Depends(require_roles(ADMIN, INVENTORY_MANAGER, FINANCE_MANAGER))):
    q = db.query(PurchaseOrder)
    if supplier_id:
        q = q.filter_by(supplier_id=supplier_id)
    if status:
        q = q.filter_by(status=status)
    return paginate(q.order_by(PurchaseOrder.id.desc()), page, size)


@router.get("/purchase-orders/{po_id}", response_model=POOut)
def get_po(po_id: int, db: Session = Depends(get_db),
           _=Depends(require_roles(ADMIN, INVENTORY_MANAGER, FINANCE_MANAGER))):
    return get_or_404(db, PurchaseOrder, po_id, "Purchase order")


@router.post("/purchase-orders/{po_id}/send", response_model=POOut)
def send_po(po_id: int, db: Session = Depends(get_db), me: User = Depends(po_staff)):
    po = get_or_404(db, PurchaseOrder, po_id, "Purchase order")
    if po.status != "draft":
        raise HTTPException(400, f"PO is {po.status}")
    po.status = "sent"
    db.commit()
    return po


@router.post("/purchase-orders/{po_id}/cancel", response_model=POOut)
def cancel_po(po_id: int, db: Session = Depends(get_db), me: User = Depends(po_staff)):
    po = get_or_404(db, PurchaseOrder, po_id, "Purchase order")
    if po.status not in ("draft", "sent"):
        raise HTTPException(400, "Can't cancel a PO that already received stock")
    po.status = "cancelled"
    db.commit()
    return po


@router.post("/purchase-orders/{po_id}/receive", response_model=POOut)
def receive_po(po_id: int, data: POReceiveIn, db: Session = Depends(get_db), me: User = Depends(po_staff)):
    po = db.query(PurchaseOrder).filter_by(id=po_id).with_for_update().first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    if po.status not in ("sent", "partially_received"):
        raise HTTPException(400, f"PO is {po.status}, send it first")
    items = {i.id: i for i in po.items}
    for line in data.lines:
        item = items.get(line.po_item_id)
        if not item:
            raise HTTPException(400, f"Item {line.po_item_id} not in this PO")
        if item.received_qty + line.quantity > item.quantity:
            raise HTTPException(400, f"Receiving more than ordered for item {item.id}")
        row = stock.get_or_create_row(db, item.product_id, item.variant_id, po.warehouse_id)
        stock.add_stock(db, row, line.quantity, "po_receipt", po.po_number, None, me.id)
        item.received_qty += line.quantity
    po.status = "received" if all(i.received_qty >= i.quantity for i in po.items) else "partially_received"
    log_action(db, me.id, "po.receive", "purchase_order", po.id, None,
               {"lines": [line.model_dump() for line in data.lines]})
    db.commit()
    return po


@router.get("/suppliers/{supplier_id}/purchase-history")
def purchase_history(supplier_id: int, db: Session = Depends(get_db),
                     _=Depends(require_roles(ADMIN, INVENTORY_MANAGER, FINANCE_MANAGER))):
    get_or_404(db, Supplier, supplier_id, "Supplier")
    pos = db.query(PurchaseOrder).filter_by(supplier_id=supplier_id).order_by(PurchaseOrder.id.desc()).all()
    total = sum(Decimal(p.total_amount) for p in pos if p.status != "cancelled")
    return {"supplier_id": supplier_id, "po_count": len(pos), "total_ordered": money(total),
            "orders": [POOut.model_validate(p) for p in pos]}


# ---------------- invoices ----------------
@router.post("/supplier-invoices", response_model=InvoiceOut, status_code=201)
def record_invoice(data: InvoiceIn, db: Session = Depends(get_db), me: User = Depends(finance)):
    po = get_or_404(db, PurchaseOrder, data.po_id, "Purchase order")
    if po.status in ("draft", "cancelled"):
        raise HTTPException(400, f"Can't invoice a {po.status} PO")
    if db.query(SupplierInvoice).filter_by(supplier_id=po.supplier_id, invoice_number=data.invoice_number).first():
        raise HTTPException(409, "This invoice number was already recorded for this supplier")
    already = db.query(func.coalesce(func.sum(SupplierInvoice.amount), 0)).filter_by(po_id=po.id).scalar()
    if money(already) + money(data.amount) > money(po.total_amount):
        raise HTTPException(400, f"Invoices would exceed PO total ({po.total_amount}), already invoiced {already}")
    inv = SupplierInvoice(supplier_id=po.supplier_id, **data.model_dump())
    db.add(inv)
    db.flush()
    log_action(db, me.id, "invoice.create", "supplier_invoice", inv.id, None, data.model_dump())
    db.commit()
    return inv


@router.get("/supplier-invoices", response_model=Page[InvoiceOut])
def list_invoices(supplier_id: Optional[int] = None, status: Optional[str] = None, page: int = 1, size: int = 20,
                  db: Session = Depends(get_db), _=Depends(finance)):
    q = db.query(SupplierInvoice)
    if supplier_id:
        q = q.filter_by(supplier_id=supplier_id)
    if status:
        q = q.filter_by(status=status)
    return paginate(q.order_by(SupplierInvoice.id.desc()), page, size)


@router.post("/supplier-invoices/{inv_id}/pay", response_model=InvoiceOut)
def pay_invoice(inv_id: int, data: InvoicePayIn, db: Session = Depends(get_db), me: User = Depends(finance)):
    inv = db.query(SupplierInvoice).filter_by(id=inv_id).with_for_update().first()
    if not inv:
        raise HTTPException(404, "Invoice not found")
    if inv.status in ("paid", "disputed"):
        raise HTTPException(400, f"Invoice is {inv.status}")
    new_paid = money(inv.paid_amount) + money(data.amount)
    if new_paid > money(inv.amount):
        raise HTTPException(400, f"Payment exceeds balance ({money(inv.amount) - money(inv.paid_amount)})")
    inv.paid_amount = new_paid
    inv.status = "paid" if new_paid == money(inv.amount) else "partially_paid"
    log_action(db, me.id, "invoice.payment", "supplier_invoice", inv.id, None, {"amount": data.amount})
    db.commit()
    return inv


@router.post("/supplier-invoices/{inv_id}/dispute", response_model=InvoiceOut)
def dispute_invoice(inv_id: int, db: Session = Depends(get_db), me: User = Depends(finance)):
    inv = get_or_404(db, SupplierInvoice, inv_id, "Invoice")
    if inv.status == "paid":
        raise HTTPException(400, "Invoice already paid")
    inv.status = "disputed"
    db.commit()
    return inv