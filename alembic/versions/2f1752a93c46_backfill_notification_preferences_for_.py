"""backfill notification preferences for existing users

Revision ID: 2f1752a93c46
Revises: 93a34442364d
Create Date: 2026-10-14 14:29:52.515728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f1752a93c46'
down_revision: Union[str, Sequence[str], None] = '93a34442364d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO notification_preferences (user_id)
            SELECT u.id
            FROM users AS u
            WHERE NOT EXISTS (
                SELECT 1
                FROM notification_preferences AS p
                WHERE p.user_id = u.id
            )
        """)
    )


def downgrade() -> None:
    # Intentionally retain preferences to avoid deleting user settings.
    pass
