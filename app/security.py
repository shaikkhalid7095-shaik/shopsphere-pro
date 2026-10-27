import uuid
from datetime import timedelta

import bcrypt
import jwt

from app.config import settings
from app.utils import now


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def _make_token(user_id: int, role: str, token_type: str, expires_delta: timedelta):
    jti = uuid.uuid4().hex
    expire = now() + expires_delta
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": token_type,
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti, expire


def create_access_token(user_id: int, role: str):
    return _make_token(user_id, role, "access", timedelta(minutes=settings.access_token_minutes))


def create_refresh_token(user_id: int, role: str):
    return _make_token(user_id, role, "refresh", timedelta(days=settings.refresh_token_days))


def decode_token(token: str) -> dict:
    # raises jwt.PyJWTError if bad / expired
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])