"""move user.is_super_user to access_level

Revision ID: 8ed9dce7fe68
Revises: 799d16d56de0
Create Date: 2022-11-28 06:37:32.654901

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "8ed9dce7fe68"
down_revision = "799d16d56de0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("access_level", sa.Integer(), nullable=False))
    op.drop_column("user", "is_super_user")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user", sa.Column("is_super_user", mysql.TINYINT(display_width=1), autoincrement=False, nullable=True)
    )
    op.drop_column("user", "access_level")
    # ### end Alembic commands ###
