"""add experiment_tag

Revision ID: ac5d82217032
Revises: 565f0f7ad445
Create Date: 2023-04-07 01:22:17.692650

"""
import sqlalchemy as sa

from alembic import op

revision = "ac5d82217032"
down_revision = "565f0f7ad445"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "experiment_tag",
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("tag", sa.String(length=50), nullable=False, comment="标签"),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.PrimaryKeyConstraint("experiment_id", "tag"),
        comment="实验标签",
    )


def downgrade() -> None:
    op.drop_table("experiment_tag")
