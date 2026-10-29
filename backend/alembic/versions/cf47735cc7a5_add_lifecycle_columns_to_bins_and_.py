"""add lifecycle columns to bins and disposal instructions

Revision ID: cf47735cc7a5
Revises: 5052a25f1027
Create Date: 2026-07-28 14:57:47.716697

"""
from alembic import op
import sqlalchemy as sa


revision = 'cf47735cc7a5'
down_revision = '5052a25f1027'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('bins', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.add_column('bins', sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('bins', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('disposal_instructions', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.add_column('disposal_instructions', sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('disposal_instructions', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))


def downgrade() -> None:
    op.drop_column('disposal_instructions', 'updated_at')
    op.drop_column('disposal_instructions', 'created_at')
    op.drop_column('disposal_instructions', 'is_active')
    op.drop_column('bins', 'updated_at')
    op.drop_column('bins', 'created_at')
    op.drop_column('bins', 'is_active')
