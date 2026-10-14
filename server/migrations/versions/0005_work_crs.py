"""Official property work CRS default; no geometry or history is rewritten."""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "farms", sa.Column("work_crs", sa.String(32), nullable=False, server_default="EPSG:32723")
    )


def downgrade():
    raise RuntimeError("Não remover configuração cartográfica; restaure backup separado.")
