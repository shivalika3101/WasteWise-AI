"""baseline schema

Revision ID: 1257784c7df9
Revises: 
Create Date: 2026-07-18 18:29:39.499823

"""
from alembic import op
import sqlalchemy as sa


revision = '1257784c7df9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('bins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('colour', sa.String(length=20), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('display_name', sa.String(length=80), nullable=True),
    sa.Column('model_label_index', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('model_label_index'),
    sa.UniqueConstraint('name')
    )
    op.create_table('category_bins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('bin_id', sa.Integer(), nullable=False),
    sa.Column('is_primary', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.ForeignKeyConstraint(['bin_id'], ['bins.id'], name='fk_bin', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_category', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('category_id', 'bin_id', name='unique_category_bin')
    )
    op.create_table('disposal_instructions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('instructions', sa.Text(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_instruction_category', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('predictions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_ref', sa.String(length=255), nullable=True),
    sa.Column('predicted_category_id', sa.Integer(), nullable=True),
    sa.Column('confidence', sa.Numeric(precision=5, scale=4), nullable=True),
    sa.Column('chosen_bin_id', sa.Integer(), nullable=True),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['chosen_bin_id'], ['bins.id'], name='fk_prediction_bin'),
    sa.ForeignKeyConstraint(['predicted_category_id'], ['categories.id'], name='fk_prediction_category'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_predictions_created_at'), 'predictions', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_predictions_created_at'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_table('disposal_instructions')
    op.drop_table('category_bins')
    op.drop_table('categories')
    op.drop_table('bins')
