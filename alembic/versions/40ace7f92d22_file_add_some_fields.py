"""file add some fields

Revision ID: 40ace7f92d22
Revises: 7998b9bc1dfe
Create Date: 2022-12-06 01:45:24.398555

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "40ace7f92d22"
down_revision = "7998b9bc1dfe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("file", sa.Column("extension", sa.String(length=50), nullable=False))
    op.add_column("file", sa.Column("index", sa.Integer(), nullable=False))
    op.add_column("file", sa.Column("size", sa.Float(), nullable=False))
    op.add_column("file", sa.Column("is_original", sa.Boolean(), nullable=False))
    op.create_index(op.f("ix_file_index"), "file", ["index"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_file_index"), table_name="file")
    op.drop_column("file", "is_original")
    op.drop_column("file", "size")
    op.drop_column("file", "index")
    op.drop_column("file", "extension")
    # ### end Alembic commands ###
