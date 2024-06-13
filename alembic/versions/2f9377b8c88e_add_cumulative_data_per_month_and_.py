"""add cumulative_data_per_month and modified dataset

Revision ID: 2f9377b8c88e
Revises: 6c54801bec54
Create Date: 2024-05-30 19:45:23.287675

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "2f9377b8c88e"
down_revision = "6c54801bec54"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cumulative_data_per_month",
        sa.Column("date", sa.Date(), nullable=False, comment="日期"),
        sa.Column("full_data_size", sa.Float(), nullable=True, comment="数据总量(GB)"),
        sa.Column("full_data_count", sa.Float(), nullable=True, comment="数据条目"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.PrimaryKeyConstraint("id"),
        comment="数据总量",
    )
    op.add_column("dataset", sa.Column("source", sa.Text(), nullable=True, comment="数据来源"))
    op.add_column("dataset", sa.Column("download_started_date", sa.Date(), nullable=True, comment="开始获取的日期"))
    op.add_column("dataset", sa.Column("planed_finish_date", sa.Date(), nullable=True, comment="计划完成日期"))
    op.add_column("dataset", sa.Column("contactor", sa.Text(), nullable=True, comment="联系人"))
    op.add_column("dataset", sa.Column("is_public", sa.Boolean(), nullable=True, comment="是否公开"))
    op.add_column("dataset", sa.Column("other_species", sa.Text(), nullable=True, comment="其他物种名称"))
    op.add_column("dataset", sa.Column("title", sa.Text(), nullable=True, comment="数据集名称"))
    op.add_column("dataset", sa.Column("planed_download_per_month", sa.Float(), nullable=True, comment="每月计划下载量"))
    op.add_column("dataset", sa.Column("is_cleaned", sa.Boolean(), nullable=True, comment="是否清洗过数据"))
    op.drop_column("dataset", "file_acquired_size_gb")
    op.alter_column(
        "eeg_data",
        "data_update_year",
        existing_type=mysql.DATETIME(),
        type_=sa.Date(),
        existing_comment="数据上传时间",
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "eeg_data",
        "data_update_year",
        existing_type=sa.Date(),
        type_=mysql.DATETIME(),
        existing_comment="数据上传时间",
        existing_nullable=False,
    )
    op.add_column("dataset", sa.Column("file_acquired_size_gb", mysql.FLOAT(), nullable=True, comment="已获取数据(GB)"))
    op.drop_column("dataset", "is_cleaned")
    op.drop_column("dataset", "planed_download_per_month")
    op.drop_column("dataset", "title")
    op.drop_column("dataset", "other_species")
    op.drop_column("dataset", "is_public")
    op.drop_column("dataset", "contactor")
    op.drop_column("dataset", "planed_finish_date")
    op.drop_column("dataset", "download_started_date")
    op.drop_column("dataset", "source")
    op.drop_table("cumulative_data_per_month")
    # ### end Alembic commands ###