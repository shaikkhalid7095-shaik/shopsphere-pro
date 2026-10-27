# Module 46 audit logs, 47 dashboard, 48 reports, 49 exports & background jobs
import os
from datetime import date, datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import AuditLog, BackgroundJob, Inventory, Payment, Product, Refund, User
from app.roles import (ADMIN, DELIVERY_MANAGER, FINANCE_MANAGER, INVENTORY_MANAGER, ORDER_MANAGER,
                       PRODUCT_MANAGER, SUPER_ADMIN)
from app.schemas.common import ORM, Page
from app.services import reports
from app.services.jobs import create_job, run_job
from app.utils import get_or_404, money, paginate

router = APIRouter(tags=["46. Audit, 47. Dashboard, 48. Reports, 49. Exports & Jobs"])
report_viewers = require_roles(ADMIN, FINANCE_MANAGER)


class AuditOut(ORM):
    id: int
    actor_id: Optional[int]
    action: str
    entity: Optional[str]
    entity_id: Optional[str]
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    created_at: datetime


class ExportIn(BaseModel):
    report: Literal["sales", "inventory", "payments", "refunds", "products"]
    format: Literal["csv", "xlsx", "pdf"] = "csv"
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: Optional[str] = None
    category_id: Optional[int] = None
    warehouse_id: Optional[int] = None


class JobOut(ORM):
    id: int
    job_type: str
    status: str
    params: Optional[dict]
    result: Optional[str]
    error: Optional[str]
    attempts: int
    max_attempts: int
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


# ---------------- audit ----------------
@router.get("/audit-logs", response_model=Page[AuditOut])
def audit_logs(entity: Optional[str] = None, entity_id: Optional[str] = None, actor_id: Optional[int] = None,
               action: Optional[str] = None, page: int = 1, size: int = 50, db: Session = Depends(get_db),
               _=Depends(require_roles(ADMIN))):
    # read only - there are deliberately no update/delete endpoints for audit logs
    q = db.query(AuditLog)
    if entity:
        q = q.filter_by(entity=entity)
    if entity_id:
        q = q.filter_by(entity_id=entity_id)
    if actor_id:
        q = q.filter_by(actor_id=actor_id)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    return paginate(q.order_by(AuditLog.id.desc()), page, size)


# ---------------- dashboard ----------------
@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db),
              me: User = Depends(require_roles(ADMIN, FINANCE_MANAGER, INVENTORY_MANAGER, ORDER_MANAGER,
                                               PRODUCT_MANAGER, DELIVERY_MANAGER))):
    """each role only gets the blocks that make sense for them"""
    role = me.role_name
    full = role in (SUPER_ADMIN, ADMIN)
    out = {"role": role}

    if full or role in (PRODUCT_MANAGER, INVENTORY_MANAGER):
        out["products"] = {
            "total": db.query(Product).count(),
            "active": db.query(Product).filter(Product.is_active.is_(True)).count(),
        }
        inv = db.query(func.coalesce(func.sum(Inventory.quantity), 0),
                       func.coalesce(func.sum(Inventory.reserved), 0)).one()
        low = [r for r in reports.inventory_report(db) if r["low_stock"]]
        out["inventory"] = {"units_on_hand": int(inv[0]), "units_reserved": int(inv[1]),
                            "low_stock_rows": len(low), "low_stock_sample": low[:5]}

    if full or role in (ORDER_MANAGER, DELIVERY_MANAGER, FINANCE_MANAGER):
        out["orders_by_status"] = reports.order_status_counts(db)
        out["returns"] = reports.returns_summary(db)

    if full or role == FINANCE_MANAGER:
        revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.status == "succeeded").scalar()
        refunded = db.query(func.coalesce(func.sum(Refund.amount), 0)).filter(Refund.status == "succeeded").scalar()
        pay_status = dict(db.query(Payment.status, func.count(Payment.id)).group_by(Payment.status).all())
        out["revenue"] = {"collected": money(revenue), "refunded": money(refunded),
                          "net": money(money(revenue) - money(refunded)), "payments_by_status": pay_status}
    return out


# ---------------- reports ----------------
@router.get("/reports/sales")
def sales(date_from: Optional[date] = None, date_to: Optional[date] = None, status: Optional[str] = None,
          category_id: Optional[int] = None, db: Session = Depends(get_db), _=Depends(report_viewers)):
    rows = reports.sales_report(db, date_from, date_to, status, category_id)
    total = sum(money(r["revenue"]) for r in rows)
    return {"rows": rows, "total_orders": sum(r["orders"] for r in rows), "total_revenue": money(total),
            "by_status": reports.order_status_counts(db, date_from, date_to)}


@router.get("/reports/inventory")
def inventory(warehouse_id: Optional[int] = None, category_id: Optional[int] = None, db: Session = Depends(get_db),
              _=Depends(require_roles(ADMIN, INVENTORY_MANAGER, FINANCE_MANAGER))):
    rows = reports.inventory_report(db, warehouse_id, category_id)
    return {"rows": rows, "total_on_hand": sum(r["on_hand"] for r in rows),
            "low_stock": sum(1 for r in rows if r["low_stock"])}


@router.get("/reports/payments")
def payments(date_from: Optional[date] = None, date_to: Optional[date] = None, status: Optional[str] = None,
             db: Session = Depends(get_db), _=Depends(report_viewers)):
    pays = reports.payments_report(db, date_from, date_to, status)
    refs = reports.refunds_report(db, date_from, date_to)
    return {"payments": pays, "refunds": refs,
            "total_paid": money(sum(money(p["amount"]) for p in pays if p["status"] == "succeeded")),
            "total_refunded": money(sum(money(r["amount"]) for r in refs if r["status"] == "succeeded"))}


@router.get("/reports/products")
def product_perf(date_from: Optional[date] = None, date_to: Optional[date] = None, category_id: Optional[int] = None,
                 db: Session = Depends(get_db), _=Depends(require_roles(ADMIN, FINANCE_MANAGER, PRODUCT_MANAGER))):
    return {"products": reports.product_performance(db, date_from, date_to, category_id),
            "categories": reports.category_performance(db, date_from, date_to)}


# ---------------- exports & jobs ----------------
@router.post("/reports/export", response_model=JobOut, status_code=202)
def export_report(data: ExportIn, background: BackgroundTasks, db: Session = Depends(get_db),
                  me: User = Depends(require_roles(ADMIN, FINANCE_MANAGER, INVENTORY_MANAGER))):
    filters = data.model_dump(exclude={"report", "format"}, exclude_none=True, mode="json")
    job = create_job(db, "report_export", {"report": data.report, "format": data.format, "filters": filters}, me.id)
    background.add_task(run_job, job.id)
    return job


@router.post("/jobs/daily-summary", response_model=JobOut, status_code=202)
def trigger_summary(background: BackgroundTasks, db: Session = Depends(get_db), me: User = Depends(require_roles(ADMIN))):
    job = create_job(db, "daily_summary", {}, me.id)
    background.add_task(run_job, job.id)
    return job


@router.post("/jobs/process-notifications", response_model=JobOut, status_code=202)
def trigger_outbox(background: BackgroundTasks, db: Session = Depends(get_db), me: User = Depends(require_roles(ADMIN))):
    job = create_job(db, "process_outbox", {}, me.id)
    background.add_task(run_job, job.id)
    return job


@router.get("/jobs", response_model=Page[JobOut])
def list_jobs(status: Optional[str] = None, job_type: Optional[str] = None, page: int = 1, size: int = 20,
              db: Session = Depends(get_db), _=Depends(report_viewers)):
    q = db.query(BackgroundJob)
    if status:
        q = q.filter_by(status=status)
    if job_type:
        q = q.filter_by(job_type=job_type)
    return paginate(q.order_by(BackgroundJob.id.desc()), page, size)


@router.get("/jobs/{job_id}", response_model=JobOut)
def job_status(job_id: int, db: Session = Depends(get_db), _=Depends(report_viewers)):
    return get_or_404(db, BackgroundJob, job_id, "Job")


@router.post("/jobs/{job_id}/retry", response_model=JobOut, status_code=202)
def retry_job(job_id: int, background: BackgroundTasks, db: Session = Depends(get_db),
              _=Depends(report_viewers)):
    job = get_or_404(db, BackgroundJob, job_id, "Job")
    if job.status != "failed":
        raise HTTPException(400, "Only failed jobs can be retried")
    if job.attempts >= job.max_attempts:
        raise HTTPException(400, f"Job already tried {job.attempts} times")
    job.status = "queued"
    db.commit()
    background.add_task(run_job, job.id)
    return job


@router.get("/jobs/{job_id}/download")
def download_export(job_id: int, db: Session = Depends(get_db), _=Depends(report_viewers)):
    job = get_or_404(db, BackgroundJob, job_id, "Job")
    if job.job_type != "report_export" or job.status != "success":
        raise HTTPException(400, f"Export not ready (status: {job.status})")
    if not job.result or not os.path.exists(job.result):
        raise HTTPException(404, "Export file missing")
    return FileResponse(job.result, filename=os.path.basename(job.result))