"""add an aoptional 'error_message' field to Task

Revision ID: 26299cf5a3b2
Revises: 
Create Date: 2024-11-27 16:09:14.473532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26299cf5a3b2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Task', sa.Column('error_message', sa.String(), nullable = True))


def downgrade():
    op.drop_column("Task", "error_message")
