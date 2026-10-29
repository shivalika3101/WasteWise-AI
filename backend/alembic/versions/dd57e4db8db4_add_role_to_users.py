"""add role to users

Revision ID: dd57e4db8db4
Revises: e31d6a20c8f4
Create Date: 2026-07-28 14:32:45.332679

"""
from alembic import op
import sqlalchemy as sa


revision = 'dd57e4db8db4'
down_revision = 'e31d6a20c8f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(length=20), server_default='user', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'role')
