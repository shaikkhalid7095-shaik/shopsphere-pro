import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RevokedToken, User
from app.roles import CUSTOMER, STAFF_ROLES, SUPER_ADMIN
from app.security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_token_payload(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = decode_token(creds.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(401, "Use an access token")
    return payload


def get_current_user(payload: dict = Depends(get_token_payload), db: Session = Depends(get_db)) -> User:
    if db.query(RevokedToken).filter_by(jti=payload["jti"]).first():
        raise HTTPException(401, "Token has been revoked")
    user = db.get(User, int(payload["sub"]))
    if not user or user.status != "active":
        raise HTTPException(401, "User not found or inactive")
    return user


def require_roles(*roles):
    """Usage: user = Depends(require_roles(ADMIN, PRODUCT_MANAGER)). super admin always passes."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role_name == SUPER_ADMIN or user.role_name in roles:
            return user
        raise HTTPException(403, "You don't have permission for this action")

    return checker


def require_staff(user: User = Depends(get_current_user)) -> User:
    if user.role_name not in STAFF_ROLES:
        raise HTTPException(403, "Staff only")
    return user


def require_customer(user: User = Depends(get_current_user)) -> User:
    if user.role_name != CUSTOMER:
        raise HTTPException(403, "Customers only")
    return user


def is_staff(user: User) -> bool:
    return user.role_name in STAFF_ROLES


def check_owner(user: User, owner_id: int, *allowed_roles):
    # customers can only touch their own data, listed staff roles can see everything
    if user.id == owner_id:
        return
    if user.role_name == SUPER_ADMIN or user.role_name in allowed_roles:
        return
    raise HTTPException(404, "Not found")