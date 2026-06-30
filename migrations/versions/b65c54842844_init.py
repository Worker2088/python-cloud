"""init

Revision ID: b65c54842844
Revises:
Create Date: 2026-05-26 14:21:13.252038

"""

from typing import Sequence, Union



revision: str = "b65c54842844"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
