"""стр-ра без таблиц folder и files

Revision ID: 650de4d16f3d
Revises: 5386a82c416c
Create Date: 2026-06-10 10:13:31.014622

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "650de4d16f3d"
down_revision: Union[str, Sequence[str], None] = "5386a82c416c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f("ix_files_s3_key"), table_name="files")
    op.drop_index(op.f("ix_files_user_folder"), table_name="files")
    op.drop_table("files")
    op.drop_index(op.f("ix_folders_user_parent"), table_name="folders")
    op.drop_table("folders")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "folders",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(length=1024), autoincrement=False, nullable=False),
        sa.Column("parent_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["folders.id"],
            name=op.f("folders_parent_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("folders_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("folders_pkey")),
        sa.UniqueConstraint(
            "name",
            "parent_id",
            "user_id",
            name=op.f("uq_folder_unique_name"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.create_index(
        op.f("ix_folders_user_parent"),
        "folders",
        ["user_id", "parent_id"],
        unique=False,
    )
    op.create_table(
        "files",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("folder_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=1024), autoincrement=False, nullable=False),
        sa.Column(
            "s3_key", sa.VARCHAR(length=1024), autoincrement=False, nullable=False
        ),
        sa.Column("size", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["folder_id"], ["folders.id"], name=op.f("files_folder_id_fkey")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("files_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("files_pkey")),
        sa.UniqueConstraint(
            "name",
            "folder_id",
            "user_id",
            name=op.f("uq_file_unique_name"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.create_index(
        op.f("ix_files_user_folder"), "files", ["user_id", "folder_id"], unique=False
    )
    op.create_index(op.f("ix_files_s3_key"), "files", ["s3_key"], unique=False)
