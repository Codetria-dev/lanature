"""add pet image columns

Revision ID: 20260418_0002
Revises: 20260417_0001
Create Date: 2026-04-18 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260418_0002"
down_revision: Union[str, None] = "20260417_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to pets table
    with op.batch_alter_table("pets", schema=None) as batch_op:
        batch_op.add_column(sa.Column("image_url", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("image_updated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove the columns
    with op.batch_alter_table("pets", schema=None) as batch_op:
        batch_op.drop_column("image_url")
        batch_op.drop_column("image_updated_at")
