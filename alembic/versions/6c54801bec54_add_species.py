"""add_species

Revision ID: 6c54801bec54
Revises: fc790ff29f0a
Create Date: 2024-04-11 18:57:11.061706

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "6c54801bec54"
down_revision = "fc790ff29f0a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "species",
        sa.Column("chinese_name", sa.Text(), nullable=False, comment="中文名称"),
        sa.Column("english_name", sa.Text(), nullable=False, comment="英文名称"),
        sa.Column("latin_name", sa.String(length=255), nullable=False, comment="拉丁文名称"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("latin_name"),
        comment="物种名称",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("species")
    # ### end Alembic commands ###
