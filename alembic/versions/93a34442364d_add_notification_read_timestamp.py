"""add notification read timestamp

Revision ID: 93a34442364d
Revises: c8d412f892f3
Create Date: 2026-10-13 16:28:02.443835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93a34442364d'
down_revision: Union[str, Sequence[str], None] = 'c8d412f892f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Add notification read timestamp."""
    op.add_column(
        "notifications",
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove notification read timestamp."""
    op.drop_column("notifications", "read_at")

