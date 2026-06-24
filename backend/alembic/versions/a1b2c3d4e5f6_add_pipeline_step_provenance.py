"""Add pipeline step provenance columns

Revision ID: a1b2c3d4e5f6
Revises: e25bf7f9506d
Create Date: 2026-06-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'e25bf7f9506d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('pipeline_steps', sa.Column('group_identifier', sa.String(), nullable=True))
    op.add_column('pipeline_steps', sa.Column('source_pipeline_slug', sa.String(), nullable=True))


def downgrade():
    op.drop_column('pipeline_steps', 'source_pipeline_slug')
    op.drop_column('pipeline_steps', 'group_identifier')
