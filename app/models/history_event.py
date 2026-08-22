from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class HistoryEvent(Base):
    __tablename__ = "history_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_tasks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    rule_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_rules.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitoring_snapshots.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    previous_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    current_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    event_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    task = relationship(
        "MonitoringTask",
        back_populates="history_events",
    )

    rule = relationship(
        "MonitoringRule",
        back_populates="history_events",
    )

    snapshot = relationship(
        "MonitoringSnapshot",
        back_populates="history_events",
    )