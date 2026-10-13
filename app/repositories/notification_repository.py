from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.history_event import HistoryEvent
from app.models.monitoring_task import MonitoringTask
from app.models.notification import Notification


class NotificationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.add(notification)
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def find_by_id(
        self,
        notification_id: int,
    ) -> Notification | None:
        statement = select(Notification).where(
            Notification.id == notification_id,
        )
        return self.db.scalar(statement)

    def find_by_id_for_user(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification | None:
        statement = (
            select(Notification)
            .join(
                HistoryEvent,
                Notification.history_event_id == HistoryEvent.id,
            )
            .join(
                MonitoringTask,
                HistoryEvent.task_id == MonitoringTask.id,
            )
            .options(
                joinedload(Notification.history_event)
                .joinedload(HistoryEvent.task),
            )
            .where(
                Notification.id == notification_id,
                MonitoringTask.user_id == user_id,
            )
        )
        return self.db.scalar(statement)

    def list_for_user(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .join(
                HistoryEvent,
                Notification.history_event_id == HistoryEvent.id,
            )
            .join(
                MonitoringTask,
                HistoryEvent.task_id == MonitoringTask.id,
            )
            .options(
                joinedload(Notification.history_event)
                .joinedload(HistoryEvent.task),
            )
            .where(
                MonitoringTask.user_id == user_id,
            )
            .order_by(
                Notification.created_at.desc(),
                Notification.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def list_by_history_event(
        self,
        history_event_id: int,
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .where(
                Notification.history_event_id == history_event_id,
            )
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_by_history_event_for_user(
        self,
        history_event_id: int,
        user_id: int,
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .join(
                HistoryEvent,
                Notification.history_event_id == HistoryEvent.id,
            )
            .join(
                MonitoringTask,
                HistoryEvent.task_id == MonitoringTask.id,
            )
            .where(
                Notification.history_event_id == history_event_id,
                MonitoringTask.user_id == user_id,
            )
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_pending(
        self,
        limit: int = 100,
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .options(
                joinedload(Notification.history_event)
                .joinedload(HistoryEvent.task)
                .joinedload(MonitoringTask.user),
            )
            .where(
                Notification.notification_status == "PENDING",
            )
            .order_by(
                Notification.created_at.asc(),
                Notification.id.asc(),
            )
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def update(
        self,
        notification: Notification,
    ) -> Notification:
        self.db.flush()
        self.db.refresh(notification)
        return notification
 
    def delete(
        self,
        notification: Notification,
    ) -> None:
        self.db.delete(notification)
        self.db.flush()
