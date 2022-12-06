"""experiment assistant

Revision ID: 7998b9bc1dfe
Revises: e41244aac5ad
Create Date: 2022-12-05 15:52:03.610302

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "7998b9bc1dfe"
down_revision = "e41244aac5ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "experiment_assistant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("gmt_create", sa.DateTime(timezone=True), nullable=True),
        sa.Column("gmt_modified", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_experiment_assistant_experiment_id"),
        "experiment_assistant",
        ["experiment_id"],
        unique=False,
    )
    op.drop_index("ix_experiment_operator_experiment_id", table_name="experiment_operator")
    op.drop_table("experiment_operator")
    op.add_column("experiment", sa.Column("main_operator", sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("experiment", "main_operator")
    op.create_table(
        "experiment_operator",
        sa.Column("id", mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("gmt_create", mysql.DATETIME(), nullable=True),
        sa.Column("gmt_modified", mysql.DATETIME(), nullable=True),
        sa.Column("is_deleted", mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
        sa.Column("user_id", mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("experiment_id", mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "is_main_operator", mysql.TINYINT(display_width=1), autoincrement=False, nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index(
        "ix_experiment_operator_experiment_id",
        "experiment_operator",
        ["experiment_id"],
        unique=False,
    )
    op.drop_index(op.f("ix_experiment_assistant_experiment_id"), table_name="experiment_assistant")
    op.drop_table("experiment_assistant")
    # ### end Alembic commands ###
