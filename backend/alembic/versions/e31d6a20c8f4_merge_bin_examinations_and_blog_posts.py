"""merge bin examinations and blog posts heads

Revision ID: e31d6a20c8f4
Revises: c9bf854a46d7, 7c99729491da
Create Date: 2026-07-28 09:00:00.000000

"""


revision = "e31d6a20c8f4"
down_revision = ("c9bf854a46d7", "7c99729491da")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This revision joins two independent feature migrations; no schema change is needed.
    pass


def downgrade() -> None:
    pass
