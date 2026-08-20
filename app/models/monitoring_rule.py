from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MonitoringRule(Base):
    __tablename__ = "monitoring_rules"

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("monitoring_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rule_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    operator: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    target_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    task = relationship(
        "MonitoringTask",
        back_populates="monitoring_rules",
    )