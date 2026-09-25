from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    history_event_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "history_events.id",
            ondelete="CASCADE",
            name="fk_notifications_history_events",
        ),
        nullable=False,
        index=True,
    )

    notification_channel: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    notification_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
        index=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    history_event = relationship(
        "HistoryEvent",
        back_populates="notifications",
    )