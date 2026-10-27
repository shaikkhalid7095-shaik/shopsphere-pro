# Module 4: Customer profile + Module 5: Addresses
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import Address, DeactivationRequest, ProfileHistory, User
from app.roles import ADMIN, SUPPORT_AGENT
from app.schemas.common import Page
from app.schemas.users import (AddressIn, AddressOut, DeactivationIn, DeactivationOut, DeactivationReview,
                               ProfileHistoryOut, ProfileUpdate, UserOut)
from app.services.audit import log_action, track
from app.utils import get_or_404, now, paginate

router = APIRouter(tags=["4. Profile & 5. Addresses"])


# ---------------- profile ----------------
@router.get("/profile", response_model=UserOut)
def my_profile(user: User = Depends(get_current_user)):
    return user


@router.patch("/profile", response_model=UserOut)
def update_profile(data: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    changes = data.model_dump(exclude_unset=True)
    if "email" in changes:
        changes["email"] = changes["email"].lower()
        if db.query(User).filter(User.email == changes["email"], User.id != user.id).first():
            raise HTTPException(409, "Email already used by another account")
    if changes.get("phone") and db.query(User).filter(User.phone == changes["phone"], User.id != user.id).first():
        raise HTTPException(409, "Phone already used by another account")

    for field, value in changes.items():
        old = getattr(user, field)
        if old == value:
            continue
        db.add(ProfileHistory(user_id=user.id, field=field, old_value=old, new_value=value, changed_by=user.id))
        setattr(user, field, value)
        if field == "email":
            # new email needs verifying again
            user.is_email_verified = False
    track(db, user.id, "profile_update", ",".join(changes.keys()))
    db.commit()
    return user


@router.get("/profile/history", response_model=Page[ProfileHistoryOut])
def my_profile_history(page: int = 1, size: int = 20, user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    q = db.query(ProfileHistory).filter_by(user_id=user.id).order_by(ProfileHistory.id.desc())
    return paginate(q, page, size)


@router.post("/profile/deactivation-request", response_model=DeactivationOut, status_code=201)
def request_deactivation(data: DeactivationIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(DeactivationRequest).filter_by(user_id=user.id, status="pending").first():
        raise HTTPException(409, "You already have a pending request")
    req = DeactivationRequest(user_id=user.id, reason=data.reason)
    db.add(req)
    track(db, user.id, "deactivation_requested")
    db.commit()
    return req


@router.get("/customers/deactivation-requests", response_model=Page[DeactivationOut])
def list_deactivation_requests(status: str = "pending", page: int = 1, size: int = 20,
                               db: Session = Depends(get_db), _=Depends(require_roles(ADMIN, SUPPORT_AGENT))):
    q = db.query(DeactivationRequest).filter_by(status=status).order_by(DeactivationRequest.id)
    return paginate(q, page, size)


@router.post("/customers/deactivation-requests/{req_id}/review", response_model=DeactivationOut)
def review_deactivation(req_id: int, data: DeactivationReview, db: Session = Depends(get_db),
                        me: User = Depends(require_roles(ADMIN, SUPPORT_AGENT))):
    req = get_or_404(db, DeactivationRequest, req_id, "Request")
    if req.status != "pending":
        raise HTTPException(400, "Already reviewed")
    req.status = "approved" if data.approve else "rejected"
    req.reviewed_by = me.id
    req.reviewed_at = now()
    if data.approve:
        target = db.get(User, req.user_id)
        target.status = "inactive"
        log_action(db, me.id, "user.deactivated", "user", target.id, {"status": "active"}, {"status": "inactive"})
    db.commit()
    return req


@router.get("/customers/{user_id}", response_model=UserOut)
def get_customer(user_id: int, db: Session = Depends(get_db), _=Depends(require_roles(ADMIN, SUPPORT_AGENT))):
    # personal info only visible to admin / support
    return get_or_404(db, User, user_id, "Customer")


# ---------------- addresses ----------------
def _my_address(db, user, address_id):
    addr = db.get(Address, address_id)
    if not addr or addr.user_id != user.id or addr.is_deleted:
        raise HTTPException(404, "Address not found")
    return addr


def _clear_default(db, user_id, address_type, keep_id=None):
    q = db.query(Address).filter_by(user_id=user_id, address_type=address_type, is_default=True)
    if keep_id:
        q = q.filter(Address.id != keep_id)
    q.update({"is_default": False})


@router.get("/addresses", response_model=list[AddressOut])
def list_addresses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Address).filter_by(user_id=user.id, is_deleted=False).order_by(Address.id).all()


@router.post("/addresses", response_model=AddressOut, status_code=201)
def add_address(data: AddressIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    has_any = db.query(Address).filter_by(user_id=user.id, address_type=data.address_type, is_deleted=False).count()
    addr = Address(user_id=user.id, **data.model_dump())
    if not has_any:
        addr.is_default = True  # first address becomes default
    db.add(addr)
    db.flush()
    if addr.is_default:
        _clear_default(db, user.id, addr.address_type, keep_id=addr.id)
    db.commit()
    return addr


@router.put("/addresses/{address_id}", response_model=AddressOut)
def update_address(address_id: int, data: AddressIn, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    addr = _my_address(db, user, address_id)
    for k, v in data.model_dump().items():
        setattr(addr, k, v)
    if addr.is_default:
        _clear_default(db, user.id, addr.address_type, keep_id=addr.id)
    db.commit()
    return addr


@router.post("/addresses/{address_id}/default", response_model=AddressOut)
def set_default(address_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    addr = _my_address(db, user, address_id)
    _clear_default(db, user.id, addr.address_type, keep_id=addr.id)
    addr.is_default = True
    db.commit()
    return addr


@router.delete("/addresses/{address_id}", status_code=204)
def delete_address(address_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    addr = _my_address(db, user, address_id)
    # soft delete because old orders reference it
    addr.is_deleted = True
    addr.is_default = False
    db.commit()