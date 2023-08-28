"""delete file table

Revision ID: 2f68cf9ba0a2
Revises: 5a840b6cfdfb
Create Date: 2023-04-25 15:46:32.442415

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

revision = "2f68cf9ba0a2"
down_revision = "5a840b6cfdfb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("task_ibfk_2", "task", type_="foreignkey")
    op.create_foreign_key("task_ibfk_2", "task", "virtual_file", ["source_file"], ["id"])
    op.drop_constraint("task_step_ibfk_2", "task_step", type_="foreignkey")
    op.create_foreign_key("task_step_ibfk_2", "task_step", "virtual_file", ["result_file_id"], ["id"])
    op.drop_table("file")


def downgrade() -> None:
    op.create_table(
        "file",
        sa.Column("experiment_id", mysql.INTEGER(), autoincrement=False, nullable=False, comment="实验ID"),
        sa.Column("paradigm_id", mysql.INTEGER(), autoincrement=False, nullable=True, comment="范式ID，null表示不属于范式而属于实验"),
        sa.Column("name", mysql.VARCHAR(length=255), nullable=False, comment="逻辑路径"),
        sa.Column("extension", mysql.VARCHAR(length=50), nullable=False, comment="文件扩展名"),
        sa.Column("size", mysql.FLOAT(), nullable=False, comment="同一实验下的文件序号"),
        sa.Column(
            "is_original", mysql.TINYINT(display_width=1), autoincrement=False, nullable=False, comment="是否是设备产生的原始文件"
        ),
        sa.Column("id", mysql.INTEGER(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column(
            "gmt_create", mysql.DATETIME(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False, comment="创建时间"
        ),
        sa.Column(
            "gmt_modified",
            mysql.DATETIME(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="修改时间",
        ),
        sa.Column(
            "is_deleted",
            mysql.TINYINT(display_width=1),
            server_default=sa.text("'0'"),
            autoincrement=False,
            nullable=False,
            comment="该行是否被删除",
        ),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"], name="file_ibfk_1"),
        sa.ForeignKeyConstraint(["paradigm_id"], ["paradigm.id"], name="file_ibfk_2"),
        sa.PrimaryKeyConstraint("id"),
        comment="文件",
    )
    op.create_index("ix_file_paradigm_id", "file", ["paradigm_id"], unique=False)
    op.create_index("ix_file_experiment_id", "file", ["experiment_id"], unique=False)
    op.drop_constraint("task_step_ibfk_2", "task_step", type_="foreignkey")
    op.create_foreign_key("task_step_result_file_id", "task_step", "file", ["result_file_id"], ["id"])
    op.drop_constraint("task_ibfk_2", "task", type_="foreignkey")
    op.create_foreign_key("task_ibfk_2", "task", "file", ["source_file"], ["id"])
