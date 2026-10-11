
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.history_event import HistoryEvent
from app.models.monitoring_task import MonitoringTask
from app.models.notification import Notification


class DashboardRepository:
    """Database queries for dashboard metrics."""

    def __init__(self, db: Session):
        self.db = db

    def get_total_tasks(self, user_id) -> int:
        statement = select(func.count(MonitoringTask.id)).where(
            MonitoringTask.user_id == user_id
        )
        return self.db.scalar(statement) or 0

    def get_active_tasks(self, user_id) -> int:
        statement = select(func.count(MonitoringTask.id)).where(
            MonitoringTask.user_id == user_id,
            MonitoringTask.is_active.is_(True),
        )
        return self.db.scalar(statement) or 0

    def get_paused_tasks(self, user_id) -> int:
        statement = select(func.count(MonitoringTask.id)).where(
            MonitoringTask.user_id == user_id,
            MonitoringTask.is_active.is_(False),
        )
        return self.db.scalar(statement) or 0

    def get_recent_events(self, user_id, since: datetime) -> int:
        statement = (
            select(func.count(HistoryEvent.id))
            .join(
                MonitoringTask,
                HistoryEvent.task_id == MonitoringTask.id,
            )
            .where(
                MonitoringTask.user_id == user_id,
                HistoryEvent.detected_at >= since,
            )
        )
        return self.db.scalar(statement) or 0

    def get_pending_notifications(self, user_id) -> int:
        statement = (
            select(func.count(Notification.id))
            .join(
                HistoryEvent,
                Notification.history_event_id == HistoryEvent.id,
            )
            .join(
                MonitoringTask,
                HistoryEvent.task_id == MonitoringTask.id,
            )
            .where(
                MonitoringTask.user_id == user_id,
                Notification.notification_status == "PENDING",
            )
        )
        return self.db.scalar(statement) or 0
