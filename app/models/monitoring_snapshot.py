from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MonitoringSnapshot(Base):
    __tablename__ = "monitoring_snapshots"

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

    snapshot_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    execution_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    task = relationship(
        "MonitoringTask",
        back_populates="monitoring_snapshots",
    )

    history_events = relationship(
        "HistoryEvent",
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )