from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.history_event import HistoryEvent
from app.repositories.history_event_repository import (
    HistoryEventRepository,
)


class HistoryEventService:

    def __init__(self, db: Session):
        self.db = db
        self.event_repository = HistoryEventRepository(db)

    def create_event(
        self,
        task_id: int,
        rule_id: int,
        snapshot_id: int,
        event_type: str,
        previous_value: str | None,
        current_value: str | None,
        event_message: str | None,
    ) -> HistoryEvent:

        event = HistoryEvent(
            task_id=task_id,
            rule_id=rule_id,
            snapshot_id=snapshot_id,
            event_type=event_type.strip(),
            previous_value=previous_value,
            current_value=current_value,
            event_message=event_message,
        )

        try:
            event = self.event_repository.create(event)

            self.db.commit()
            self.db.refresh(event)

            return event

        except Exception:
            self.db.rollback()
            raise

    def get_event(
        self,
        event_id: int,
        task_id: int,
    ) -> HistoryEvent:

        event = self.event_repository.find_by_id(
            event_id,
        )

        if event is None or event.task_id != task_id:
            raise ResourceNotFoundError(
                "History event not found."
            )

        return event

    def list_events(
        self,
        task_id: int,
    ) -> list[HistoryEvent]:

        return self.event_repository.list_by_task(
            task_id,
        )