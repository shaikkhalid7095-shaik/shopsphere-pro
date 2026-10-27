# Module 2: User management (staff side)
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Permission, Role, User, UserActivity
from app.roles import ADMIN, SUPER_ADMIN
from app.schemas.common import Page
from app.schemas.users import (ActivityOut, RoleAssignIn, RoleOut, RolePermissionsIn, StatusIn, UserCreate,
                               UserOut, UserUpdate)
from app.security import hash_password
from app.services.audit import log_action, track
from app.utils import get_or_404, paginate

router = APIRouter(prefix="/users", tags=["2. User Management"])
admin_only = require_roles(ADMIN)


def _get_role(db, name):
    role = db.query(Role).filter_by(name=name).first()
    if not role:
        raise HTTPException(400, f"Unknown role '{name}'")
    return role


@router.get("", response_model=Page[UserOut])
def list_users(search: Optional[str] = None, role: Optional[str] = None, status: Optional[str] = None,
               page: int = 1, size: int = 20, db: Session = Depends(get_db), _=Depends(admin_only)):
    q = db.query(User)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(User.full_name.ilike(like), User.email.ilike(like), User.phone.ilike(like)))
    if role:
        q = q.join(Role).filter(Role.name == role)
    if status:
        q = q.filter(User.status == status)
    return paginate(q.order_by(User.id.desc()), page, size)


@router.post("", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), me: User = Depends(admin_only)):
    if data.role == SUPER_ADMIN and me.role_name != SUPER_ADMIN:
        raise HTTPException(403, "Only super admin can create another super admin")
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(409, "Email already exists")
    if data.phone and db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(409, "Phone already exists")
    role = _get_role(db, data.role)
    user = User(full_name=data.full_name, email=data.email.lower(), phone=data.phone,
                password_hash=hash_password(data.password), role_id=role.id,
                is_email_verified=True, registration_status="completed")
    db.add(user)
    db.flush()
    log_action(db, me.id, "user.create", "user", user.id, None, {"email": user.email, "role": role.name})
    db.commit()
    db.refresh(user)
    return user


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), _=Depends(admin_only)):
    return db.query(Role).order_by(Role.id).all()


@router.put("/roles/{role_name}/permissions", response_model=RoleOut)
def set_role_permissions(role_name: str, data: RolePermissionsIn, db: Session = Depends(get_db),
                         me: User = Depends(require_roles())):  # super admin only
    role = _get_role(db, role_name)
    perms = []
    for code in data.permissions:
        perm = db.query(Permission).filter_by(code=code).first()
        if not perm:
            perm = Permission(code=code)
            db.add(perm)
        perms.append(perm)
    old = [p.code for p in role.permissions]
    role.permissions = perms
    log_action(db, me.id, "role.permissions", "role", role.id, old, data.permissions)
    db.commit()
    return role


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    return get_or_404(db, User, user_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), me: User = Depends(admin_only)):
    user = get_or_404(db, User, user_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("phone") and db.query(User).filter(User.phone == changes["phone"], User.id != user.id).first():
        raise HTTPException(409, "Phone already used")
    old = {k: getattr(user, k) for k in changes}
    for k, v in changes.items():
        setattr(user, k, v)
    log_action(db, me.id, "user.update", "user", user.id, old, changes)
    db.commit()
    return user


@router.put("/{user_id}/role", response_model=UserOut)
def assign_role(user_id: int, data: RoleAssignIn, db: Session = Depends(get_db), me: User = Depends(admin_only)):
    user = get_or_404(db, User, user_id)
    if (data.role == SUPER_ADMIN or user.role_name == SUPER_ADMIN) and me.role_name != SUPER_ADMIN:
        raise HTTPException(403, "Only super admin can change super admin roles")
    role = _get_role(db, data.role)
    old = user.role_name
    user.role_id = role.id
    user.role = role
    log_action(db, me.id, "user.role_change", "user", user.id, {"role": old}, {"role": role.name})
    db.commit()
    return user


@router.put("/{user_id}/status", response_model=UserOut)
def set_status(user_id: int, data: StatusIn, db: Session = Depends(get_db), me: User = Depends(admin_only)):
    user = get_or_404(db, User, user_id)
    if user.id == me.id:
        raise HTTPException(400, "You can't change your own status")
    if user.role_name == SUPER_ADMIN and me.role_name != SUPER_ADMIN:
        raise HTTPException(403, "Can't change super admin")
    old = user.status
    user.status = data.status
    log_action(db, me.id, "user.status_change", "user", user.id, {"status": old}, {"status": data.status})
    track(db, user.id, "status_changed", f"{old} -> {data.status} by user {me.id}")
    db.commit()
    return user


@router.delete("/{user_id}", response_model=UserOut)
def deactivate_user(user_id: int, db: Session = Depends(get_db), me: User = Depends(admin_only)):
    # soft delete only, orders etc still point to the user
    return set_status(user_id, StatusIn(status="inactive"), db, me)


@router.get("/{user_id}/activity", response_model=Page[ActivityOut])
def user_activity(user_id: int, page: int = 1, size: int = 20, db: Session = Depends(get_db),
                  _=Depends(admin_only)):
    get_or_404(db, User, user_id)
    q = db.query(UserActivity).filter_by(user_id=user_id).order_by(UserActivity.id.desc())
    return paginate(q, page, size)