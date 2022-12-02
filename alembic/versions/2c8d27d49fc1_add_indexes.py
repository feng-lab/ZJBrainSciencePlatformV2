"""add indexes

Revision ID: 2c8d27d49fc1
Revises: 5e514e211841
Create Date: 2022-12-02 02:32:10.225491

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2c8d27d49fc1"
down_revision = "5e514e211841"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        op.f("ix_experiment_operator_experiment_id"),
        "experiment_operator",
        ["experiment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_file_experiment_id"), "file", ["experiment_id"], unique=False
    )
    op.create_index(op.f("ix_file_path"), "file", ["path"], unique=False)
    op.create_index(
        op.f("ix_paradigm_experiment_id"), "paradigm", ["experiment_id"], unique=False
    )
    op.create_index(
        op.f("ix_paradigm_file_file_id"), "paradigm_file", ["file_id"], unique=False
    )
    op.create_index(
        op.f("ix_paradigm_file_paradigm_id"),
        "paradigm_file",
        ["paradigm_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_paradigm_file_paradigm_id"), table_name="paradigm_file")
    op.drop_index(op.f("ix_paradigm_file_file_id"), table_name="paradigm_file")
    op.drop_index(op.f("ix_paradigm_experiment_id"), table_name="paradigm")
    op.drop_index(op.f("ix_file_path"), table_name="file")
    op.drop_index(op.f("ix_file_experiment_id"), table_name="file")
    op.drop_index(
        op.f("ix_experiment_operator_experiment_id"), table_name="experiment_operator"
    )
    # ### end Alembic commands ###
