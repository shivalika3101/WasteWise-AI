"""add timestamps to category bins

Revision ID: 658023d88c42
Revises: cf47735cc7a5
Create Date: 2026-07-28 15:08:54.708535

"""
from alembic import op
import sqlalchemy as sa


revision = '658023d88c42'
down_revision = 'cf47735cc7a5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('category_bins', sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('category_bins', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))


def downgrade() -> None:
    op.drop_column('category_bins', 'updated_at')
    op.drop_column('category_bins', 'created_at')
