"""add browser push subscriptions

Revision ID: 3426d3e40817
Revises: 1cf64d98f84c
Create Date: 2026-10-03 21:03:31.233086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3426d3e40817'
down_revision: Union[str, Sequence[str], None] = '1cf64d98f84c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'browser_push_subscriptions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('endpoint', sa.Text(), nullable=False),
        sa.Column('p256dh_key', sa.String(length=255), nullable=False),
        sa.Column('auth_key', sa.String(length=255), nullable=False),
        sa.Column('expiration_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_browser_push_subscriptions_users',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'endpoint',
            name='uq_browser_push_subscriptions_endpoint',
        ),
    )
    op.create_index(
        op.f('ix_browser_push_subscriptions_user_id'),
        'browser_push_subscriptions',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_browser_push_subscriptions_user_id'),
        table_name='browser_push_subscriptions',
    )
    op.drop_table('browser_push_subscriptions')
