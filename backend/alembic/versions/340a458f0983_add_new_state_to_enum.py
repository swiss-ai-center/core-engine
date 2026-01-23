"""Add new state to enum

Revision ID: 340a458f0983
Revises: 904327f640c7
Create Date: 2026-01-23 15:07:32.510484

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '340a458f0983'
down_revision = '904327f640c7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    if bind.dialect.name == 'postgresql':
        # Add new value to the enum in PostgreSQL
        op.execute("ALTER TYPE executionunitstatus ADD VALUE IF NOT EXISTS 'SLEEPING'")

    # SQLite stores enums as strings, so no action needed


def downgrade():
    # Note: PostgreSQL doesn't support removing enum values directly
    pass
