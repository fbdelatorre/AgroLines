"""Independent licensing tables; existing accounts, GIS and history stay intact."""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "license_subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan", sa.String(12), nullable=False),
        sa.Column("edition", sa.String(20), nullable=False),
        sa.Column("expires", sa.Integer, nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.CheckConstraint("plan IN ('monthly','annual')"),
        sa.CheckConstraint("status IN ('active','suspended','revoked')"),
        sa.CheckConstraint("edition IN ('individual','professional','enterprise')"),
    )
    op.create_index("ix_license_subscriptions_user_id", "license_subscriptions", ["user_id"])
    op.create_table(
        "license_slots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "subscription_id",
            sa.String(36),
            sa.ForeignKey("license_subscriptions.id"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("current_activation", sa.String(36)),
        sa.UniqueConstraint("subscription_id", "position"),
        sa.CheckConstraint("position IN (1,2)"),
    )
    op.create_index("ix_license_slots_subscription_id", "license_slots", ["subscription_id"])
    op.create_table(
        "license_activations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("slot_id", sa.String(36), sa.ForeignKey("license_slots.id"), nullable=False),
        sa.Column("installation_id", sa.String(36), nullable=False),
        sa.Column("device_label", sa.String(80), nullable=False),
        sa.Column("credential_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("revoked", sa.Boolean, nullable=False),
        sa.Column("generation", sa.Integer, nullable=False),
        sa.Column("created", sa.Integer, nullable=False),
        sa.Column("checked", sa.Integer, nullable=False),
    )
    op.create_index("ix_license_activations_slot_id", "license_activations", ["slot_id"])
    op.create_table(
        "license_administrators",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role", sa.String(12), nullable=False),
        sa.Column("totp_sealed", sa.LargeBinary, nullable=False),
        sa.Column("last_counter", sa.Integer, nullable=False),
        sa.CheckConstraint("role IN ('viewer','manager','owner')"),
    )
    op.create_table(
        "license_admin_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("license_administrators.user_id"),
            nullable=False,
        ),
        sa.Column("expires", sa.Integer, nullable=False),
    )
    op.create_index("ix_license_admin_sessions_user_id", "license_admin_sessions", ["user_id"])


def downgrade():
    raise RuntimeError("Não eliminar assinaturas/ativações. Restaure backup em ambiente separado.")
