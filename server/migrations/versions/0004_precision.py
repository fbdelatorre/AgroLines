"""Add native-coordinate storage and precision provenance without rewriting versions."""

import sqlalchemy as sa
from alembic import op

from server.spatial_type import NativeGeometry

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    # Historical records retain their originals. No reconstructed coordinates or
    # invented precision reports are substituted for existing source data.
    op.add_column("plot_versions", sa.Column("native_geometry", NativeGeometry(), nullable=True))
    op.add_column("plot_versions", sa.Column("precision_report", sa.JSON(), nullable=True))


def downgrade():
    raise RuntimeError("Downgrade removeria proveniência de precisão; restaure backup separado.")
