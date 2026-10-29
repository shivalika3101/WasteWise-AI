"""add bin examinations

Revision ID: c9bf854a46d7
Revises: 7ba10b1226b3
Create Date: 2026-07-27 17:06:26.649728

"""
from alembic import op
import sqlalchemy as sa


revision = 'c9bf854a46d7'
down_revision = '7ba10b1226b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'bin_examinations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('prediction_id', sa.Integer(), nullable=False),
        sa.Column('selected_bin_id', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], name='fk_bin_examination_prediction', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['selected_bin_id'], ['bins.id'], name='fk_bin_examination_bin'),
    )
    op.create_index('ix_bin_examinations_prediction_id', 'bin_examinations', ['prediction_id'])


def downgrade() -> None:
    op.drop_index('ix_bin_examinations_prediction_id', table_name='bin_examinations')
    op.drop_table('bin_examinations')
