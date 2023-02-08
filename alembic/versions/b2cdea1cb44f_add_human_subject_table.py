"""add human_subject table

Revision ID: b2cdea1cb44f
Revises: 86c548e3656b
Create Date: 2023-02-08 07:27:39.568144

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b2cdea1cb44f"
down_revision = "86c548e3656b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "human_subject",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("gender", sa.Enum("male", "female", name="gender"), nullable=True, comment="性别"),
        sa.Column("birthdate", sa.Date(), nullable=True, comment="出生日期"),
        sa.Column("death_date", sa.Date(), nullable=True, comment="死亡日期"),
        sa.Column("education", sa.String(length=50), nullable=True, comment="教育程度"),
        sa.Column("occupation", sa.String(length=50), nullable=True, comment="职业"),
        sa.Column(
            "marital_status",
            sa.Enum("unmarried", "married", name="maritalstatus"),
            nullable=True,
            comment="婚姻状况",
        ),
        sa.Column(
            "abo_blood_type",
            sa.Enum("A", "B", "AB", "O", name="abobloodtype"),
            nullable=True,
            comment="ABO血型",
        ),
        sa.Column("is_left_handed", sa.Boolean(), nullable=True, comment="是否是左撇子"),
        sa.Column("phone_number", sa.String(length=50), nullable=True, comment="电话号码"),
        sa.Column("email", sa.String(length=100), nullable=True, comment="电子邮箱地址"),
        sa.Column("address", sa.String(length=255), nullable=True, comment="住址"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column(
            "gmt_create",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "gmt_modified",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="修改时间",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
            comment="该行是否被删除",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="被试者",
    )
    op.create_index(op.f("ix_human_subject_user_id"), "human_subject", ["user_id"], unique=True)
    op.create_table(
        "experiment_human_subject",
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("human_subject_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.ForeignKeyConstraint(["human_subject_id"], ["human_subject.id"]),
        sa.PrimaryKeyConstraint("experiment_id", "human_subject_id"),
        comment="实验包含的被试者",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("experiment_human_subject")
    op.drop_index(op.f("ix_human_subject_user_id"), table_name="human_subject")
    op.drop_table("human_subject")
    # ### end Alembic commands ###
