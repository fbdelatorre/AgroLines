from uuid import uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.crs import DEFAULT_WORK_CRS
from server.db import Base
from server.spatial_type import NativeGeometry, PolygonGeometry


def new_id() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Credential(Base):
    __tablename__ = "credentials"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    password_hash: Mapped[str] = mapped_column(Text)


class AuthSession(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    access_hash: Mapped[str] = mapped_column(String(64), unique=True)
    refresh_hash: Mapped[str] = mapped_column(String(64), unique=True)
    access_expires: Mapped[int] = mapped_column(Integer)
    refresh_expires: Mapped[int] = mapped_column(Integer)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)


class ResetToken(Base):
    __tablename__ = "password_resets"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    expires: Mapped[int] = mapped_column(Integer)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class RateBucket(Base):
    __tablename__ = "rate_buckets"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    started: Mapped[int] = mapped_column(Integer)
    attempts: Mapped[int] = mapped_column(Integer, default=0)


class Farm(Base):
    __tablename__ = "farms"
    work_crs: Mapped[str] = mapped_column(
        String(32), default=DEFAULT_WORK_CRS, server_default=DEFAULT_WORK_CRS
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))


class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))


class Operation(Base):
    __tablename__ = "operations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    season_id: Mapped[str] = mapped_column(ForeignKey("seasons.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))


class Invitation(Base):
    __tablename__ = "invitations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.id"), index=True)
    inviter_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    recipient_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    expires: Mapped[int] = mapped_column(Integer)


class InvitationScope(Base):
    __tablename__ = "invitation_scopes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    invitation_id: Mapped[str] = mapped_column(ForeignKey("invitations.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    season_id: Mapped[str | None] = mapped_column(ForeignKey("seasons.id"))
    operation_id: Mapped[str | None] = mapped_column(ForeignKey("operations.id"))
    __table_args__ = (
        CheckConstraint("operation_id IS NULL OR season_id IS NOT NULL"),
        CheckConstraint("role IN ('administrator','editor','operator','viewer')"),
    )


class Permission(Base):
    __tablename__ = "permissions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    invitation_id: Mapped[str] = mapped_column(ForeignKey("invitations.id"))
    role: Mapped[str] = mapped_column(String(20))
    season_id: Mapped[str | None] = mapped_column(ForeignKey("seasons.id"))
    operation_id: Mapped[str | None] = mapped_column(ForeignKey("operations.id"))
    __table_args__ = (
        CheckConstraint("operation_id IS NULL OR season_id IS NOT NULL"),
        CheckConstraint("role IN ('administrator','editor','operator','viewer')"),
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str | None] = mapped_column(String(36))
    farm_id: Mapped[str | None] = mapped_column(ForeignKey("farms.id"), index=True)
    occurred: Mapped[int] = mapped_column(Integer)


# Stage 3.1: append-only geometry versions; existing Stage 2 tables are unchanged.
class Plot(Base):
    __tablename__ = "plots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    current_revision: Mapped[int] = mapped_column(Integer)
    fingerprint: Mapped[str] = mapped_column(String(64))
    __table_args__ = (UniqueConstraint("farm_id", "fingerprint", name="uq_plot_geometry"),)


class PlotVersion(Base):
    __tablename__ = "plot_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created: Mapped[int] = mapped_column(Integer)
    geometry: Mapped[dict] = mapped_column(PolygonGeometry())
    original_geometry: Mapped[dict] = mapped_column(JSON)
    native_geometry: Mapped[dict | None] = mapped_column(NativeGeometry())
    precision_report: Mapped[dict | None] = mapped_column(JSON)
    source_crs: Mapped[str] = mapped_column(Text)
    metric_crs: Mapped[str] = mapped_column(String(32))
    attributes: Mapped[dict] = mapped_column(JSON)
    area_m2: Mapped[float] = mapped_column(Float)
    perimeter_m: Mapped[float] = mapped_column(Float)
    __table_args__ = (
        UniqueConstraint("plot_id", "revision", name="uq_plot_revision"),
        Index("ix_plot_versions_geometry", "geometry", postgresql_using="gist"),
    )


class ImportSource(Base):
    __tablename__ = "import_sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.id"), index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("farm_id", "sha256", name="uq_source_content"),)


class VersionSource(Base):
    __tablename__ = "version_sources"
    version_id: Mapped[str] = mapped_column(ForeignKey("plot_versions.id"), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("import_sources.id"), primary_key=True)


class PlotSeason(Base):
    __tablename__ = "plot_seasons"
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), primary_key=True)
    season_id: Mapped[str] = mapped_column(ForeignKey("seasons.id"), primary_key=True)


class PlotOperation(Base):
    __tablename__ = "plot_operations"
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), primary_key=True)
    operation_id: Mapped[str] = mapped_column(ForeignKey("operations.id"), primary_key=True)


class LicenseSubscription(Base):
    __tablename__ = "license_subscriptions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    plan: Mapped[str] = mapped_column(String(12))
    edition: Mapped[str] = mapped_column(String(20), default="individual")
    expires: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(12), default="active")
    __table_args__ = (
        CheckConstraint("plan IN ('monthly','annual')"),
        CheckConstraint("status IN ('active','suspended','revoked')"),
        CheckConstraint("edition IN ('individual','professional','enterprise')"),
    )


class LicenseSlot(Base):
    __tablename__ = "license_slots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    subscription_id: Mapped[str] = mapped_column(ForeignKey("license_subscriptions.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    current_activation: Mapped[str | None] = mapped_column(String(36), nullable=True)
    __table_args__ = (
        UniqueConstraint("subscription_id", "position"),
        CheckConstraint("position IN (1,2)"),
    )


class LicenseActivation(Base):
    __tablename__ = "license_activations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slot_id: Mapped[str] = mapped_column(ForeignKey("license_slots.id"), index=True)
    installation_id: Mapped[str] = mapped_column(String(36))
    device_label: Mapped[str] = mapped_column(String(80))
    credential_hash: Mapped[str] = mapped_column(String(64), unique=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    generation: Mapped[int] = mapped_column(Integer, default=0)
    created: Mapped[int] = mapped_column(BigInteger)
    checked: Mapped[int] = mapped_column(BigInteger)


class LicenseAdministrator(Base):
    __tablename__ = "license_administrators"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(12))
    totp_sealed: Mapped[bytes] = mapped_column(LargeBinary)
    last_counter: Mapped[int] = mapped_column(Integer, default=-1)
    __table_args__ = (CheckConstraint("role IN ('viewer','manager','owner')"),)


class LicenseAdminSession(Base):
    __tablename__ = "license_admin_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("license_administrators.user_id"), index=True)
    expires: Mapped[int] = mapped_column(BigInteger)
