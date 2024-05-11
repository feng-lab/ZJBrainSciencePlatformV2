"""modified_dataset

Revision ID: ee8f1867aa17
Revises: 6c54801bec54
Create Date: 2024-05-11 10:25:09.619172

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "ee8f1867aa17"
down_revision = "6c54801bec54"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("dataset", sa.Column("source", sa.Text(), nullable=True, comment="数据来源"))
    op.add_column("dataset", sa.Column("download_started_date", sa.Date(), nullable=True, comment="开始获取的日期"))
    op.add_column("dataset", sa.Column("planed_finish_date", sa.Date(), nullable=True, comment="计划完成日期"))
    op.add_column("dataset", sa.Column("contactor", sa.Text(), nullable=True, comment="联系人"))
    op.add_column("dataset", sa.Column("is_public", sa.Boolean(), nullable=True, comment="是否公开"))
    op.add_column("dataset", sa.Column("other_species", sa.Text(), nullable=True, comment="其他物种名称"))
    op.add_column("dataset", sa.Column("title", sa.Text(), nullable=True, comment="数据集名称"))
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
    op.drop_column("dataset", "title")
    op.drop_column("dataset", "other_species")
    op.drop_column("dataset", "is_public")
    op.drop_column("dataset", "contactor")
    op.drop_column("dataset", "planed_finish_date")
    op.drop_column("dataset", "download_started_date")
    op.drop_column("dataset", "source")
    # ### end Alembic commands ###
