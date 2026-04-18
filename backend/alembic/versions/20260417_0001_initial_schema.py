"""initial schema

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17 00:00:00
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm

from app.database import Base
from app import models  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "20260417_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    # Drop in reverse dependency order for safety.
    metadata = Base.metadata
    with orm.Session(bind=bind):
        for table in reversed(metadata.sorted_tables):
            table.drop(bind=bind, checkfirst=True)
