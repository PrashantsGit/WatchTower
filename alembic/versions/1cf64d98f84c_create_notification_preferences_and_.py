"""create notification preferences and notifications

Revision ID: 1cf64d98f84c
Revises: ad49f4ba4b38
Create Date: 2026-09-25 13:21:12.790946

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1cf64d98f84c"
down_revision: Union[str, Sequence[str], None] = "ad49f4ba4b38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "email_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "browser_push_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "notify_on_price_change",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "notify_on_stock_change",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_notification_preferences_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_notification_preferences",
        ),
        sa.UniqueConstraint(
            "user_id",
            name="uq_notification_preferences_user_id",
        ),
    )

    op.create_table(
        "notifications",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "history_event_id",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "notification_channel",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "notification_status",
            sa.String(length=30),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column(
            "delivered_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["history_event_id"],
            ["history_events.id"],
            name="fk_notifications_history_events",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_notifications",
        ),
    )

    op.create_index(
        "idx_notifications_history_event_id",
        "notifications",
        ["history_event_id"],
        unique=False,
    )

    op.create_index(
        "idx_notifications_status",
        "notifications",
        ["notification_status"],
        unique=False,
    )

    op.create_index(
        "idx_notifications_created_at",
        "notifications",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_notifications_created_at",
        table_name="notifications",
    )

    op.drop_index(
        "idx_notifications_status",
        table_name="notifications",
    )

    op.drop_index(
        "idx_notifications_history_event_id",
        table_name="notifications",
    )

    op.drop_table("notifications")

    op.drop_table("notification_preferences")   