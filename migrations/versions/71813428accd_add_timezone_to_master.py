"""add timezone to master

Revision ID: 71813428accd
Revises: 74a67a414265
Create Date: 2026-03-22 20:26:13.899335

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "71813428accd"
down_revision: Union[str, Sequence[str], None] = "74a67a414265"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "masters",
        sa.Column(
            "timezone", sa.String(), nullable=False, server_default="Europe/Moscow"
        ),
    )


def downgrade() -> None:
    op.drop_column("masters", "timezone")
