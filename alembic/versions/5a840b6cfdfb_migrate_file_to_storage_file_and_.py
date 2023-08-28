"""migrate file to storage_file and virtual_file

Revision ID: 5a840b6cfdfb
Revises: 01b5380e17fc
Create Date: 2023-04-18 10:12:02.771024

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
        sa.Column("size", sa.Float(), nullable=False, comment="所有相关文件的大小之和"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.ForeignKeyConstraint(["paradigm_id"], ["paradigm.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="虚拟文件",
    )
    op.create_index(op.f("ix_virtual_file_experiment_id"), "virtual_file", ["experiment_id"], unique=False)
    op.create_index(op.f("ix_virtual_file_paradigm_id"), "virtual_file", ["paradigm_id"], unique=False)
    op.create_table(
        "storage_file",
        sa.Column("virtual_file_id", sa.Integer(), nullable=False, comment="虚拟文件ID"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="文件名"),
        sa.Column("size", sa.Float(), nullable=False, comment="文件大小"),
        sa.Column("storage_path", sa.String(length=255), nullable=False, comment="文件系统存储路径"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["virtual_file_id"], ["virtual_file.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="实际文件",
    )
    op.create_index(op.f("ix_storage_file_virtual_file_id"), "storage_file", ["virtual_file_id"], unique=False)

    op.execute("BEGIN;")
    op.execute(
        """ INSERT INTO virtual_file (
                id, 
                gmt_create, 
                gmt_modified, 
                is_deleted, 
                experiment_id, 
                paradigm_id, 
                name, 
                file_type, 
                is_original, 
                size) 
            SELECT 
                id,
                gmt_create,
                gmt_modified,
                is_deleted,
                experiment_id,
                paradigm_id,
                name,
                extension,
                is_original,
                size
            FROM file
            WHERE is_deleted = FALSE;"""
    )
    op.execute(
        """ INSERT INTO storage_file (
                gmt_create, 
                gmt_modified, 
                is_deleted, 
                virtual_file_id, 
                name, 
                size, 
                storage_path)
            SELECT 
                gmt_create, 
                gmt_modified, 
                is_deleted, 
                id, 
                name, 
                size, 
                CONCAT(experiment_id, '/', IF(extension = '', id, CONCAT(id, '.', extension))) AS storage_path
        FROM file
        WHERE is_deleted = FALSE;"""
    )
    op.execute("COMMIT;")


def downgrade() -> None:
    op.execute("BEGIN;")
    op.execute(
        """ INSERT INTO file (
                id,
                experiment_id,
                paradigm_id,
                name,
                extension,
                size,
                is_original,
                gmt_create,
                gmt_modified,
                is_deleted)
            SELECT 
                virtual_file.id,
                virtual_file.experiment_id,
                virtual_file.paradigm_id,
                virtual_file.name,
                virtual_file.file_type,
                virtual_file.size,
                virtual_file.is_original,
                virtual_file.gmt_create,
                virtual_file.gmt_modified,
                FALSE
            FROM virtual_file INNER JOIN storage_file ON virtual_file.id = storage_file.virtual_file_id
            WHERE 
                virtual_file.is_deleted = FALSE
                AND storage_file.is_deleted = FALSE
                AND storage_file.name = virtual_file.name;"""
    )
    op.execute("COMMIT;")
    op.drop_table("storage_file")
    op.drop_table("virtual_file")
