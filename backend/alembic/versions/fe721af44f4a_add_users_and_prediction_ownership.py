"""add users and prediction ownership

Revision ID: fe721af44f4a
Revises: 1257784c7df9
Create Date: 2026-07-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'fe721af44f4a'
down_revision = '1257784c7df9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.add_column('predictions', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_predictions_user_id'), 'predictions', ['user_id'], unique=False)
    op.create_foreign_key('fk_prediction_user', 'predictions', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_prediction_user', 'predictions', type_='foreignkey')
    op.drop_index(op.f('ix_predictions_user_id'), table_name='predictions')
    op.drop_column('predictions', 'user_id')
    op.drop_table('users')