# Module 1 (auth) + Module 3 (customer registration)
import secrets
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user, get_token_payload
from app.models import RefreshToken, RevokedToken, Role, User
from app.roles import CUSTOMER
from app.schemas.common import Message
from app.schemas.users import (ChangePasswordIn, LoginIn, RefreshIn, RegisterIn, RegisterOut, TokenOut,
                               UserOut)
from app.security import (create_access_token, create_refresh_token, decode_token, hash_password,
                          verify_password)
from app.services.audit import track
from app.services.notify import queue_message
from app.utils import now

router = APIRouter(prefix="/auth", tags=["1. Auth & 3. Registration"])


def _issue_tokens(db, user):
    access, _, _ = create_access_token(user.id, user.role_name)
    refresh, jti, exp = create_refresh_token(user.id, user.role_name)
    db.add(RefreshToken(user_id=user.id, jti=jti, expires_at=exp))
    return TokenOut(access_token=access, refresh_token=refresh, role=user.role_name)


@router.post("/register", response_model=RegisterOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email is already registered")
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(409, "Phone number is already registered")

    role = db.query(Role).filter_by(name=CUSTOMER).first()
    if not role:
        raise HTTPException(500, "Roles not seeded. Run: python seed.py")

    token = secrets.token_urlsafe(24)
    user = User(full_name=data.full_name, email=email, phone=data.phone,
                password_hash=hash_password(data.password), role_id=role.id,
                status="active", registration_status="pending_verification",
                is_email_verified=False, email_verify_token=token)
    db.add(user)
    db.flush()
    link = f"/auth/verify-email?token={token}"
    queue_message(db, "email", email, "Verify your ShopSphere account",
                  f"Hi {data.full_name}, verify your email here: {link}", template="verification")
    track(db, user.id, "register")
    db.commit()
    return RegisterOut(id=user.id, email=user.email, registration_status=user.registration_status,
                       message="Registered. Please verify your email.",
                       verify_token=token if settings.debug else None)


@router.get("/verify-email", response_model=Message)
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email_verify_token == token).first()
    if not user:
        raise HTTPException(400, "Invalid or used verification token")
    user.is_email_verified = True
    user.email_verify_token = None
    user.registration_status = "completed"
    track(db, user.id, "email_verified")
    db.commit()
    return {"message": "Email verified"}


@router.post("/resend-verification", response_model=Message)
def resend_verification(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.is_email_verified:
        raise HTTPException(400, "Email already verified")
    user.email_verify_token = secrets.token_urlsafe(24)
    queue_message(db, "email", user.email, "Verify your ShopSphere account",
                  f"Verify here: /auth/verify-email?token={user.email_verify_token}", template="verification")
    db.commit()
    return {"message": "Verification email sent"}


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    # same endpoint for customers and employees, role comes back in the response
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Wrong email or password")
    if user.status != "active":
        raise HTTPException(403, f"Account is {user.status}")
    user.last_login_at = now()
    tokens = _issue_tokens(db, user)
    track(db, user.id, "login")
    db.commit()
    return tokens


@router.post("/refresh", response_model=TokenOut)
def refresh(data: RefreshIn, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Not a refresh token")
    row = db.query(RefreshToken).filter_by(jti=payload["jti"]).first()
    if not row or row.revoked:
        raise HTTPException(401, "Refresh token revoked")
    user = db.get(User, int(payload["sub"]))
    if not user or user.status != "active":
        raise HTTPException(401, "User inactive")
    # rotate: old refresh token can't be used again
    row.revoked = True
    tokens = _issue_tokens(db, user)
    db.commit()
    return tokens


@router.post("/logout", response_model=Message)
def logout(data: RefreshIn | None = None, payload: dict = Depends(get_token_payload),
           user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(RevokedToken(jti=payload["jti"], expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc).replace(tzinfo=None)))
    if data and data.refresh_token:
        try:
            rp = decode_token(data.refresh_token)
            db.query(RefreshToken).filter_by(jti=rp["jti"], user_id=user.id).update({"revoked": True})
        except jwt.PyJWTError:
            pass
    track(db, user.id, "logout")
    db.commit()
    return {"message": "Logged out"}


@router.post("/logout-all", response_model=Message)
def logout_all(payload: dict = Depends(get_token_payload), user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    db.query(RefreshToken).filter_by(user_id=user.id, revoked=False).update({"revoked": True})
    db.add(RevokedToken(jti=payload["jti"], expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc).replace(tzinfo=None)))
    db.commit()
    return {"message": "Logged out from all devices"}


@router.post("/change-password", response_model=Message)
def change_password(data: ChangePasswordIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(400, "Old password is wrong")
    user.password_hash = hash_password(data.new_password)
    db.query(RefreshToken).filter_by(user_id=user.id, revoked=False).update({"revoked": True})
    track(db, user.id, "password_changed")
    db.commit()
    return {"message": "Password changed, please login again on other devices"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user