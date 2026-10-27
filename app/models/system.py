from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, event

from app.database import Base
from app.utils import now


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, index=True)
    action = Column(String(80), nullable=False)
    entity = Column(String(60), index=True)
    entity_id = Column(String(40))
    old_value = Column(JSON)
    new_value = Column(JSON)
    created_at = Column(DateTime, default=now, index=True)


# audit rows are insert-only. any update / delete from the ORM blows up
@event.listens_for(AuditLog, "before_update")
def _block_audit_update(mapper, connection, target):
    raise ValueError("Audit logs cannot be modified")


@event.listens_for(AuditLog, "before_delete")
def _block_audit_delete(mapper, connection, target):
    raise ValueError("Audit logs cannot be deleted")


class ConfigHistory(Base):
    # generic history for promotions, tax rules, suppliers etc
    __tablename__ = "config_history"
    id = Column(Integer, primary_key=True)
    entity = Column(String(60), index=True)
    entity_id = Column(Integer, index=True)
    action = Column(String(30))
    data = Column(JSON)
    changed_by = Column(Integer)
    changed_at = Column(DateTime, default=now)


class BackgroundJob(Base):
    __tablename__ = "background_jobs"
    id = Column(Integer, primary_key=True)
    job_type = Column(String(50), nullable=False)  # report_export / daily_summary / process_outbox
    status = Column(String(20), default="queued")  # queued / running / success / failed
    params = Column(JSON)
    result = Column(Text)
    error = Column(Text)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=now)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)