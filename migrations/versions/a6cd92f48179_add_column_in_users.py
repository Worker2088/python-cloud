"""хэширование пароля

Revision ID: a6cd92f48179
Revises: 574edaa92e43
Create Date: 2026-05-29 10:16:19.020758

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6cd92f48179"
down_revision: Union[str, Sequence[str], None] = "574edaa92e43"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_column("users", "is_active")
