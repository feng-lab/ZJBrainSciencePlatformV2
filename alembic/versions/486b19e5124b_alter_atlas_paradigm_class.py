"""alter atlas paradigm class

Revision ID: 486b19e5124b
Revises: f7cc9d40eef1
Create Date: 2023-07-11 13:44:28.478296

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "486b19e5124b"
down_revision = "f7cc9d40eef1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "atlas_paradigm_class", sa.Column("parent_id", sa.Integer(), nullable=True, comment="父节点ID，null表示第一层节点")
    )
    op.alter_column(
        "atlas_paradigm_class", "description", existing_type=mysql.TEXT(), nullable=False, existing_comment="描述"
    )
    op.alter_column(
        "virtual_file",
        "size",
        existing_type=mysql.FLOAT(),
        comment="显示给用户看的文件大小",
        existing_comment="所有相关文件的大小之和",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "virtual_file",
        "size",
        existing_type=mysql.FLOAT(),
        comment="所有相关文件的大小之和",
        existing_comment="显示给用户看的文件大小",
        existing_nullable=False,
    )
    op.alter_column(
        "atlas_paradigm_class", "description", existing_type=mysql.TEXT(), nullable=True, existing_comment="描述"
    )
    op.drop_column("atlas_paradigm_class", "parent_id")
