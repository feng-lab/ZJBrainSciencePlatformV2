"""file remove store_path

Revision ID: c30c0806827f
Revises: 40ace7f92d22
Create Date: 2022-12-06 03:03:04.389830

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "c30c0806827f"
down_revision = "40ace7f92d22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("file", "store_path")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("file", sa.Column("store_path", mysql.VARCHAR(length=511), nullable=False))
    # ### end Alembic commands ###
