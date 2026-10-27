"""Background jobs: report exports, scheduled summaries, notification outbox."""
import csv
import logging
import os
from datetime import date

from app.config import settings
from app.database import SessionLocal
from app.models import BackgroundJob, Order
from app.roles import ADMIN, INVENTORY_MANAGER, SUPER_ADMIN
from app.services import reports
from app.services.notify import notify_roles, process_outbox
from app.utils import now

log = logging.getLogger("shopsphere.jobs")


def _parse_filters(params):
    f = dict(params.get("filters") or {})
    for key in ("date_from", "date_to"):
        if f.get(key) and isinstance(f[key], str):
            f[key] = date.fromisoformat(f[key])
    return f


def write_export(rows, report_name, fmt, job_id):
    os.makedirs(settings.export_dir, exist_ok=True)
    path = os.path.join(settings.export_dir, f"{report_name}_report_{job_id}.{fmt}")
    headers = list(rows[0].keys()) if rows else ["no_data"]

    if fmt == "csv":
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
    elif fmt == "xlsx":
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = report_name[:30]
        ws.append(headers)
        for r in rows:
            ws.append([r.get(h) if not isinstance(r.get(h), (dict, list)) else str(r.get(h)) for h in headers])
        wb.save(path)
    elif fmt == "pdf":
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        doc = SimpleDocTemplate(path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        data = [headers] + [[str(r.get(h, "")) for h in headers] for r in rows]
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        doc.build([Paragraph(f"ShopSphere Pro - {report_name.title()} report", styles["Title"]),
                   Spacer(1, 12), table])
    else:
        raise ValueError(f"Unsupported format {fmt}")
    return path


def _do_export(db, job):
    params = job.params or {}
    name = params["report"]
    rows = reports.REPORTS[name](db, _parse_filters(params))
    return write_export(rows, name, params.get("format", "csv"), job.id)


def _do_summary(db, job):
    counts = reports.order_status_counts(db)
    low = [r for r in reports.inventory_report(db) if r["low_stock"]]
    today_orders = db.query(Order).filter(Order.created_at >= now().replace(hour=0, minute=0, second=0)).count()
    text = f"Orders today: {today_orders}. By status: {counts}. Low stock rows: {len(low)}."
    notify_roles(db, [SUPER_ADMIN, ADMIN, INVENTORY_MANAGER], "Daily summary", text, kind="general")
    return text


def _do_outbox(db, job):
    return f"processed {process_outbox(db)} messages"


HANDLERS = {"report_export": _do_export, "daily_summary": _do_summary, "process_outbox": _do_outbox}


def run_job(job_id: int):
    """runs in a background task with its own db session"""
    db = SessionLocal()
    try:
        job = db.get(BackgroundJob, job_id)
        if not job or job.status in ("running", "success"):
            return
        job.status = "running"
        job.attempts += 1
        job.started_at = now()
        db.commit()
        try:
            job.result = HANDLERS[job.job_type](db, job)
            job.status = "success"
            job.error = None
        except Exception as exc:
            db.rollback()
            job = db.get(BackgroundJob, job_id)
            job.status = "failed"
            job.error = str(exc)[:2000]
            log.exception("job %s failed", job_id)
        job.finished_at = now()
        db.commit()
    finally:
        db.close()


def create_job(db, job_type, params=None, user_id=None):
    job = BackgroundJob(job_type=job_type, params=params or {}, created_by=user_id)
    db.add(job)
    db.commit()
    return job