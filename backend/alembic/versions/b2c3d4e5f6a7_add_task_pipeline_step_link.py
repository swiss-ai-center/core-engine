"""Add pipeline_step_id link column to tasks

Gives each pipeline-execution task a stable reference back to the pipeline step
it was created for, so the frontend can pair tasks to steps reliably instead of
relying on list position. Stored as a soft reference (plain UUID, no DB-level
foreign key) on purpose: pipeline updates delete steps while only archiving the
tasks that pointed at them, so an enforced FK with no ON DELETE rule would make
those deletes fail.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tasks', sa.Column('pipeline_step_id', sa.Uuid(), nullable=True))


def downgrade():
    op.drop_column('tasks', 'pipeline_step_id')
