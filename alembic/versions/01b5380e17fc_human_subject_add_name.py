"""human_subject add name

Revision ID: 01b5380e17fc
Revises: ac5d82217032
Create Date: 2023-04-07 03:13:59.306982

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "01b5380e17fc"
down_revision = "ac5d82217032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "human_subject", sa.Column("name", sa.String(length=50), nullable=True, comment="姓名")
    )


def downgrade() -> None:
    op.drop_column("human_subject", "name")
