
"""add revoked tokens

Revision ID: c8d412f892f3
Revises: 3426d3e40817
Create Date: 2026-10-12 12:43:18.373604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8d412f892f3"
down_revision: Union[str, Sequence[str], None] = "3426d3e40817"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the revoked_tokens table."""
    op.create_table(
        "revoked_tokens",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "jti",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "jti",
            name="uq_revoked_tokens_jti",
        ),
    )

    op.create_index(
        "idx_revoked_tokens_expires_at",
        "revoked_tokens",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the revoked_tokens table."""
    op.drop_index(
        "idx_revoked_tokens_expires_at",
        table_name="revoked_tokens",
    )
    op.drop_table("revoked_tokens")
