import sqlalchemy as sa

from alembic import op

revision = "565f0f7ad445"
down_revision = "e57a7b7fec35"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "experiment",
        "type",
        type_=sa.Enum("SSVEP", "MI", "neuron", "other", name="type"),
        existing_nullable=False,
        existing_comment="实验类型",
    )


def downgrade() -> None:
    op.alter_column(
        "experiment",
        "type",
        type_=sa.Enum("SSVEP", "MI", "neuron", name="type"),
        existing_nullable=False,
        existing_comment="实验类型",
    )
