import json
from datetime import date, datetime
from decimal import Decimal

from app.models import AuditLog, ConfigHistory, UserActivity


def to_jsonable(data):
    """turn decimals/dates into plain values so they fit in a JSON column"""
    if data is None:
        return None

    def default(o):
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return str(o)

    return json.loads(json.dumps(data, default=default))


def row_to_dict(obj, fields=None):
    cols = fields or [c.name for c in obj.__table__.columns]
    return to_jsonable({c: getattr(obj, c) for c in cols})


def log_action(db, actor_id, action, entity, entity_id=None, old=None, new=None):
    db.add(AuditLog(
        actor_id=actor_id,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        old_value=to_jsonable(old),
        new_value=to_jsonable(new),
    ))


def save_history(db, entity, entity_id, action, data, user_id):
    db.add(ConfigHistory(entity=entity, entity_id=entity_id, action=action,
                         data=to_jsonable(data), changed_by=user_id))


def track(db, user_id, action, detail=None):
    db.add(UserActivity(user_id=user_id, action=action, detail=detail))