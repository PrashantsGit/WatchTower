from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.history_event import HistoryEvent
from app.models.monitoring_task import MonitoringTask


class HistoryEventRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event: HistoryEvent,
    ) -> HistoryEvent:
        self.db.add(event)
        self.db.flush()
        self.db.refresh(event)
        return event

    def find_by_id(
        self,
        event_id: int,
    ) -> HistoryEvent | None:
        statement = select(HistoryEvent).where(
            HistoryEvent.id == event_id,
        )

        return self.db.scalar(statement)

    def list_by_task(
        self,
        task_id: int,
    ) -> list[HistoryEvent]:
        statement = (
            select(HistoryEvent)
            .where(
                HistoryEvent.task_id == task_id,
            )
            .order_by(
                HistoryEvent.detected_at.desc(),
                HistoryEvent.id.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_for_user(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[HistoryEvent]:
        statement = (
            select(HistoryEvent)
            .join(
                MonitoringTask,
                MonitoringTask.id == HistoryEvent.task_id,
            )
            .where(
                MonitoringTask.user_id == user_id,
            )
            .order_by(
                HistoryEvent.detected_at.desc(),
                HistoryEvent.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def list_by_task_for_user(
        self,
        task_id: int,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[HistoryEvent]:
        statement = (
            select(HistoryEvent)
            .join(
                MonitoringTask,
                MonitoringTask.id == HistoryEvent.task_id,
            )
            .where(
                HistoryEvent.task_id == task_id,
                MonitoringTask.user_id == user_id,
            )
            .order_by(
                HistoryEvent.detected_at.desc(),
                HistoryEvent.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )