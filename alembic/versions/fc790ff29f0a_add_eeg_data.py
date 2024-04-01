"""add eeg data

Revision ID: fc790ff29f0a
Revises: a0d93a525a2a
Create Date: 2024-04-01 17:15:45.325020

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fc790ff29f0a"
down_revision = "a0d93a525a2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eeg_data",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("gender", sa.Enum("male", "female", name="gender"), nullable=False, comment="性别"),
        sa.Column("age", sa.Integer(), nullable=False, comment="年龄"),
        sa.Column("data_update_year", sa.DateTime(), nullable=False, comment="数据上传时间"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="脑电数据",
    )
    op.create_index(op.f("ix_eeg_data_user_id"), "eeg_data", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("eeg_data")
