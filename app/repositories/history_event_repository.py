from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.history_event import HistoryEvent


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
            )
        )

        return list(
            self.db.scalars(statement).all()
        )