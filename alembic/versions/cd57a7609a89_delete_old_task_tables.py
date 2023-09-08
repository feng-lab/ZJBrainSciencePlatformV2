"""delete old task tables

Revision ID: cd57a7609a89
Revises: 8dc0f8fefc93
Create Date: 2023-09-08 16:06:46.597474

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "cd57a7609a89"
down_revision = "8dc0f8fefc93"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("task_step")
    op.drop_table("task")
    op.alter_column(
        "atlas_region", "label", existing_type=mysql.VARCHAR(length=255), nullable=True, existing_comment="标签"
    )


def downgrade() -> None:
    op.alter_column(
        "atlas_region", "label", existing_type=mysql.VARCHAR(length=255), nullable=False, existing_comment="标签"
    )
    op.create_table(
        "task",
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
        sa.Column("name", mysql.VARCHAR(length=255), nullable=False, comment="任务名"),
        sa.Column("description", mysql.TEXT(), nullable=False, comment="任务描述"),
        sa.Column("source_file", mysql.INTEGER(), autoincrement=False, nullable=False, comment="任务分析的文件ID"),
        sa.Column("type", mysql.ENUM("preprocess", "analysis", "preprocess_analysis"), nullable=False, comment="任务类型"),
        sa.Column("start_at", mysql.DATETIME(), nullable=True, comment="任务开始执行的时间"),
        sa.Column("end_at", mysql.DATETIME(), nullable=True, comment="任务结束时间"),
        sa.Column(
            "status", mysql.ENUM("wait_start", "running", "done", "error", "cancelled"), nullable=False, comment="任务状态"
        ),
        sa.Column("creator", mysql.INTEGER(), autoincrement=False, nullable=False, comment="任务创建者ID"),
        sa.ForeignKeyConstraint(["creator"], ["user.id"], name="task_ibfk_1"),
        sa.ForeignKeyConstraint(["source_file"], ["virtual_file.id"], name="task_ibfk_2"),
        sa.PrimaryKeyConstraint("id"),
        comment="任务",
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_comment="任务",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_table(
        "task_step",
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
        sa.Column("task_id", mysql.INTEGER(), autoincrement=False, nullable=False, comment="任务ID"),
        sa.Column("name", mysql.VARCHAR(length=255), nullable=False, comment="步骤名字"),
        sa.Column("type", mysql.ENUM("preprocess", "analysis"), nullable=False, comment="任务步骤类型"),
        sa.Column("parameter", mysql.TEXT(), nullable=False, comment="步骤参数JSON"),
        sa.Column("index", mysql.INTEGER(), autoincrement=False, nullable=False, comment="任务中的步骤顺序"),
        sa.Column(
            "status", mysql.ENUM("wait_start", "running", "done", "error", "cancelled"), nullable=False, comment="步骤状态"
        ),
        sa.Column("start_at", mysql.DATETIME(), nullable=True, comment="步骤开始执行的时间"),
        sa.Column("end_at", mysql.DATETIME(), nullable=True, comment="步骤结束时间"),
        sa.Column("result_file_id", mysql.INTEGER(), autoincrement=False, nullable=True, comment="结果文件ID"),
        sa.Column("error_msg", mysql.VARCHAR(length=255), nullable=True, comment="错误信息"),
        sa.ForeignKeyConstraint(["result_file_id"], ["virtual_file.id"], name="task_step_ibfk_2"),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], name="task_step_ibfk_1"),
        sa.PrimaryKeyConstraint("id"),
        comment="任务步骤",
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_comment="任务步骤",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
