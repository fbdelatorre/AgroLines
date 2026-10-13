"""Estabelece a extensão PostGIS, sem criar tabelas de domínio."""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")


def downgrade() -> None:
    # Shared extension may contain user data: never remove it automatically.
    pass
