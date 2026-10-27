import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal, engine
from app.routers import (admin, attributes, auth, cart, catalog, coupons, customers, engagement, inventory,
                         logistics, marketing, notifications, orders, payments, prices, products, refunds,
                         returns, suppliers, support, users)
from app.services.jobs import create_job, run_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("shopsphere")


async def scheduler():
    """tiny scheduler: sends queued emails/sms every minute and makes a summary once a day"""
    seconds_since_summary = 0
    while True:
        await asyncio.sleep(settings.outbox_interval_seconds)
        seconds_since_summary += settings.outbox_interval_seconds
        try:
            db = SessionLocal()
            try:
                job = create_job(db, "process_outbox")
                job_id = job.id
                summary_id = None
                if seconds_since_summary >= settings.summary_interval_minutes * 60:
                    summary_id = create_job(db, "daily_summary").id
                    seconds_since_summary = 0
            finally:
                db.close()
            await asyncio.to_thread(run_job, job_id)
            if summary_id:
                await asyncio.to_thread(run_job, summary_id)
        except Exception:
            log.exception("scheduler tick failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = None
    if settings.scheduler_enabled:
        task = asyncio.create_task(scheduler())
    yield
    if task:
        task.cancel()


app = FastAPI(
    title="ShopSphere Pro API",
    description="E-commerce backend - FastAPI + MySQL + SQLAlchemy. Login at /auth/login, "
                "copy the access_token and press **Authorize**.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # e.g. someone tries to edit an audit log
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/", tags=["Health"])
def root():
    return {"app": settings.app_name, "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return JSONResponse(status_code=503, content={"status": "error", "database": str(exc)[:200]})


for r in [auth, users, customers, catalog, products, attributes, prices, inventory, cart, coupons,
          marketing, orders, payments, refunds, logistics, returns, engagement, support, notifications,
          suppliers, admin]:
    app.include_router(r.router)