"""add dataset

Revision ID: a0d93a525a2a
Revises: 8dc0f8fefc93
Create Date: 2024-03-12 10:12:56.244385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0d93a525a2a"
down_revision = "8dc0f8fefc93"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Dataset",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("description", sa.Text(), nullable=False, comment="描述"),
        sa.Column("species", sa.Text(), nullable=True, comment="物种"),
        sa.Column("paper_title", sa.Text(), nullable=True, comment="文章标题"),
        sa.Column("paper_doi", sa.Text(), nullable=True, comment="文章DOI"),
        sa.Column("development_stage", sa.Text(), nullable=True, comment="发育时期"),
        sa.Column("file_format", sa.Text(), nullable=True, comment="文件格式"),
        sa.Column("sample_count", sa.Integer(), nullable=True, comment="样本数量"),
        sa.Column("data_publisher", sa.Text(), nullable=True, comment="数据发布机构/单位"),
        sa.Column("date_update_year", sa.Date(), nullable=True, comment="数据更新年份"),
        sa.Column("file_count", sa.Integer(), nullable=True, comment="文件数量"),
        sa.Column("file_total_size_gb", sa.Float(), nullable=True, comment="数据总量(GB)"),
        sa.Column("file_acquired_size_gb", sa.Float(), nullable=True, comment="已获取数据(GB)"),
        sa.Column("associated_diseases", sa.Text(), nullable=True, comment="相关疾病"),
        sa.Column("organ", sa.Text(), nullable=True, comment="器官"),
        sa.Column("cell_count", sa.Integer(), nullable=True, comment="细胞数"),
        sa.Column("data_type", sa.Text(), nullable=True, comment="数据类型"),
        sa.Column("experiment_platform", sa.Text(), nullable=True, comment="实验、测序平台"),
        sa.Column("fetch_url", sa.Text(), nullable=True, comment="下载路径"),
        sa.Column("project", sa.Text(), nullable=True, comment="项目"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="数据集",
    )
    op.create_index(op.f("ix_Dataset_user_id"), "Dataset", ["user_id"], unique=False)
    op.create_table(
        "DatasetFile",
        sa.Column("dataset_id", sa.Integer(), nullable=False, comment="数据集id"),
        sa.Column("path", sa.Text(), nullable=False, comment="文件路径"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["dataset_id"], ["Dataset.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="数据集文件",
    )
    op.create_index(op.f("ix_DatasetFile_dataset_id"), "DatasetFile", ["dataset_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_DatasetFile_dataset_id"), table_name="DatasetFile")
    op.drop_table("DatasetFile")
    op.drop_index(op.f("ix_Dataset_user_id"), table_name="Dataset")
    op.drop_table("Dataset")
