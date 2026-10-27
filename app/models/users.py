from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import now

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = relationship("Permission", secondary=role_permissions, lazy="selectin")


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True)
    full_name = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(ForeignKey("roles.id"), nullable=False)
    # active / inactive / suspended / pending
    status = Column(String(20), default="active", nullable=False)
    registration_status = Column(String(30), default="completed")  # pending_verification / completed
    is_email_verified = Column(Boolean, default=False)
    email_verify_token = Column(String(100), index=True)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    role = relationship("Role", lazy="joined")

    @property
    def role_name(self):
        return self.role.name if self.role else None


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jti = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)


class RevokedToken(Base):
    # blacklisted access tokens (logout)
    __tablename__ = "revoked_tokens"
    id = Column(Integer, primary_key=True)
    jti = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class UserActivity(Base):
    __tablename__ = "user_activities"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    action = Column(String(100), nullable=False)
    detail = Column(String(500))
    created_at = Column(DateTime, default=now)


class ProfileHistory(Base):
    __tablename__ = "profile_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    field = Column(String(50))
    old_value = Column(String(255))
    new_value = Column(String(255))
    changed_by = Column(Integer)
    changed_at = Column(DateTime, default=now)


class DeactivationRequest(Base):
    __tablename__ = "deactivation_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    reason = Column(Text)
    status = Column(String(20), default="pending")  # pending / approved / rejected
    reviewed_by = Column(Integer)
    created_at = Column(DateTime, default=now)
    reviewed_at = Column(DateTime)


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    label = Column(String(50))
    address_type = Column(String(20), default="shipping")  # shipping / billing
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    line1 = Column(String(255), nullable=False)
    line2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(12), nullable=False)
    country = Column(String(60), default="India")
    is_default = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

    def as_text(self):
        parts = [self.full_name, self.line1, self.line2, self.city, self.state, self.postal_code, self.country, self.phone]
        return ", ".join(p for p in parts if p)