"""AtlasRegion add label

Revision ID: 8dc0f8fefc93
Revises: 486b19e5124b
Create Date: 2023-08-28 16:54:20.359665

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "8dc0f8fefc93"
down_revision = "486b19e5124b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("atlas_region", sa.Column("label", sa.String(length=255), nullable=False, comment="标签"))
    op.execute("UPDATE atlas_region SET label = CONCAT(description, '(', acronym, ')') WHERE TRUE")


def downgrade() -> None:
    op.drop_column("atlas_region", "label")
