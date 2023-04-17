"""migrate file to storage_file and virtual_file

Revision ID: 5a840b6cfdfb
Revises: 01b5380e17fc
Create Date: 2023-04-17 09:23:23.020492

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "5a840b6cfdfb"
down_revision = "01b5380e17fc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "virtual_file",
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("paradigm_id", sa.Integer(), nullable=True, comment="范式ID，null表示不属于范式而属于实验"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="文件名"),
        sa.Column("file_type", sa.String(length=50), nullable=False, comment="文件类型"),
        sa.Column("is_original", sa.Boolean(), nullable=False, comment="是否是设备产生的原始文件"),
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
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.ForeignKeyConstraint(["paradigm_id"], ["paradigm.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="虚拟文件",
    )
    op.create_index(
        op.f("ix_virtual_file_experiment_id"), "virtual_file", ["experiment_id"], unique=False
    )
    op.create_index(
        op.f("ix_virtual_file_paradigm_id"), "virtual_file", ["paradigm_id"], unique=False
    )
    op.create_table(
        "storage_file",
        sa.Column("virtual_file_id", sa.Integer(), nullable=False, comment="虚拟文件ID"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="文件名"),
        sa.Column("size", sa.Float(), nullable=False, comment="文件大小"),
        sa.Column("storage_path", sa.String(length=255), nullable=False, comment="文件系统存储路径"),
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
        sa.ForeignKeyConstraint(["virtual_file_id"], ["virtual_file.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="实际文件",
    )
    op.create_index(
        op.f("ix_storage_file_virtual_file_id"), "storage_file", ["virtual_file_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_storage_file_virtual_file_id"), table_name="storage_file")
    op.drop_table("storage_file")
    op.drop_index(op.f("ix_virtual_file_paradigm_id"), table_name="virtual_file")
    op.drop_index(op.f("ix_virtual_file_experiment_id"), table_name="virtual_file")
    op.drop_table("virtual_file")
