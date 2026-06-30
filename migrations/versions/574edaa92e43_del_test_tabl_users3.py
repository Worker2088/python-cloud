"""del users3

Revision ID: 574edaa92e43
Revises: 9c6c996e64c1
Create Date: 2026-05-26 15:41:46.824688

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "574edaa92e43"
down_revision: Union[str, Sequence[str], None] = "9c6c996e64c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("users3")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "users3",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("users3_pkey")),
    )
