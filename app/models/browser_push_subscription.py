
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BrowserPushSubscription(Base):
    __tablename__ = "browser_push_subscriptions"

    __table_args__ = (
        UniqueConstraint(
            "endpoint",
            name="uq_browser_push_subscriptions_endpoint",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
            name="fk_browser_push_subscriptions_users",
        ),
        nullable=False,
        index=True,
    )

    endpoint: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    p256dh_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    auth_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    expiration_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
