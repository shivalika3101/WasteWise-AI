"""add blog posts

Revision ID: 7c99729491da
Revises: 7ba10b1226b3
Create Date: 2026-07-27 17:21:40.701631

"""
from alembic import op
import sqlalchemy as sa


revision = '7c99729491da'
down_revision = '7ba10b1226b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'blog_posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.UniqueConstraint('slug', name='unique_blog_post_slug'),
    )


def downgrade() -> None:
    op.drop_table('blog_posts')
