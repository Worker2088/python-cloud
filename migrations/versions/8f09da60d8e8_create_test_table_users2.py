"""create table users2

Revision ID: 8f09da60d8e8
Revises: ef83ab357f37
Create Date: 2026-05-26 15:09:38.779809

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f09da60d8e8"
down_revision: Union[str, Sequence[str], None] = "ef83ab357f37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users2",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users2")
