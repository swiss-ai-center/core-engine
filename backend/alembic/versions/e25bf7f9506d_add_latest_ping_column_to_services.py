"""Add latest_ping column to services

Revision ID: e25bf7f9506d
Revises: 340a458f0983
Create Date: 2026-02-18 15:04:27.545776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e25bf7f9506d'
down_revision = '340a458f0983'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('services', sa.Column('latest_ping', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('services', 'latest_ping')
