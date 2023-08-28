"""add atlas tables

Revision ID: f7cc9d40eef1
Revises: 2f68cf9ba0a2
Create Date: 2023-07-04 16:52:00.327914

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "f7cc9d40eef1"
down_revision = "2f68cf9ba0a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "atlas",
        sa.Column("name", sa.String(length=255), nullable=False, comment="名称"),
        sa.Column("url", sa.String(length=255), nullable=False, comment="主页地址"),
        sa.Column("title", sa.String(length=255), nullable=False, comment="页面显示的标题"),
        sa.Column("whole_segment_id", sa.BigInteger(), nullable=True, comment="全脑轮廓ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱",
    )
    op.create_table(
        "atlas_behavioral_domain",
        sa.Column("name", sa.String(length=255), nullable=False, comment="名称"),
        sa.Column("value", sa.Double(), nullable=False, comment="值"),
        sa.Column("label", sa.String(length=255), nullable=False, comment="显示的名字"),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父节点ID，null表示第一层节点"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱的行为域结构数据，以树状结构存储",
    )
    op.create_table(
        "atlas_paradigm_class",
        sa.Column("name", sa.String(length=255), nullable=False, comment="名称"),
        sa.Column("value", sa.Double(), nullable=False, comment="值"),
        sa.Column("label", sa.String(length=255), nullable=False, comment="标签"),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱范例集",
    )
    op.create_table(
        "atlas_region",
        sa.Column("region_id", sa.BigInteger(), nullable=True, comment="脑区ID"),
        sa.Column("description", sa.String(length=255), nullable=False, comment="描述"),
        sa.Column("acronym", sa.String(length=255), nullable=False, comment="缩写"),
        sa.Column("lobe", sa.String(length=255), nullable=True, comment="所属脑叶"),
        sa.Column("gyrus", sa.String(length=255), nullable=True, comment="所属脑回"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父节点ID，null表示第一层节点"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱脑区构成信息，以树状结构存储",
    )
    op.create_table(
        "atlas_region_behavioral_domain",
        sa.Column("key", sa.String(length=255), nullable=False, comment="行为域"),
        sa.Column("value", sa.Double(), nullable=False, comment="行为域值"),
        sa.Column("region_id", sa.BigInteger(), nullable=False, comment="脑区ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱中与脑区相关联的行为域数据",
    )
    op.create_table(
        "atlas_region_link",
        sa.Column("link_id", sa.Integer(), nullable=False, comment="连接信息ID"),
        sa.Column("region1", sa.String(length=255), nullable=False, comment="脑区1"),
        sa.Column("region2", sa.String(length=255), nullable=False, comment="脑区2"),
        sa.Column("value", sa.Double(), nullable=True, comment="连接强度，null表示仅有连接"),
        sa.Column("opposite_value", sa.Double(), nullable=True, comment="反向连接强度，null表示仅有连接"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱脑区之间的连接强度信息",
    )
    op.create_table(
        "atlas_region_paradigm_class",
        sa.Column("key", sa.String(length=255), nullable=False, comment="范例集"),
        sa.Column("value", sa.Double(), nullable=False, comment="范例集值"),
        sa.Column("region_id", sa.BigInteger(), nullable=False, comment="脑区ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱中与脑区相关联的范例集",
    )


def downgrade() -> None:
    op.drop_table("atlas_region_paradigm_class")
    op.drop_table("atlas_region_link")
    op.drop_table("atlas_region_behavioral_domain")
    op.drop_table("atlas_region")
    op.drop_table("atlas_paradigm_class")
    op.drop_table("atlas_behavioral_domain")
    op.drop_table("atlas")
