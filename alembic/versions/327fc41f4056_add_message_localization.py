"""add message_localization

Revision ID: 327fc41f4056
Revises: 2f68cf9ba0a2
Create Date: 2023-05-05 10:37:57.825046

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "327fc41f4056"
down_revision = "2f68cf9ba0a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "message_localization",
        sa.Column("message_id", sa.String(length=50), nullable=False, comment="消息模板ID"),
        sa.Column(
            "locale",
            sa.Enum("zh_CN", "en_US", name="messagelocale"),
            nullable=False,
            comment="消息语言",
        ),
        sa.Column("template", sa.String(length=255), nullable=False, comment="消息模板内容"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column(
            "gmt_create",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "gmt_modified",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="修改时间",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
            comment="该行是否被删除",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="本地化消息",
    )
    op.create_index(
        op.f("ix_message_localization_message_id"),
        "message_localization",
        ["message_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("message_localization")
