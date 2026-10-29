"""add selected model to predictions

Revision ID: 7ba10b1226b3
Revises: fe721af44f4a
Create Date: 2026-07-26 17:17:48.472148

"""
from alembic import op
import sqlalchemy as sa


revision = '7ba10b1226b3'
down_revision = 'fe721af44f4a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('selected_model', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('predictions', 'selected_model')
