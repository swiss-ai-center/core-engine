"""add service access level

Revision ID: c3d4e5f6a7b8
Revises: 95e1ca207682
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c3d4e5f6a7b8"
down_revision = "95e1ca207682"
branch_labels = None
depends_on = None


values = ("PUBLIC", "USER", "ADMIN", "DISABLED")


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(*values, name="serviceaccesslevel").create(bind, checkfirst=True)
        column_type = postgresql.ENUM(*values, name="serviceaccesslevel", create_type=False)
    else:
        column_type = sa.Enum(*values, name="serviceaccesslevel")

    op.add_column(
        "services",
        sa.Column(
            "access_level",
            column_type,
            nullable=False,
            server_default="PUBLIC",
        ),
    )


def downgrade():
    bind = op.get_bind()
    op.drop_column("services", "access_level")
    if bind.dialect.name == "postgresql":
        postgresql.ENUM(*values, name="serviceaccesslevel").drop(bind, checkfirst=True)
