"""add is_active to users

Revision ID: 5052a25f1027
Revises: dd57e4db8db4
Create Date: 2026-07-28 14:48:19.111066

"""
from alembic import op
import sqlalchemy as sa


revision = '5052a25f1027'
down_revision = 'dd57e4db8db4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'is_active')
