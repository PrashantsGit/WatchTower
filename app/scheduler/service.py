from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.monitoring_task_repository import (
    MonitoringTaskRepository,
)


class SchedulerService:

    def __init__(
        self,
        db: Session,
        engine,
    ):
        self.db = db
        self.repository = MonitoringTaskRepository(db)
        self.engine = engine

    def run_pending(self) -> None:
        now = datetime.now(timezone.utc)

        tasks = self.repository.list_due_active_tasks(now)

        for task in tasks:
            try:
                self.engine.execute(
                    task_id=task.id,
                    user_id=task.user_id,
                )

                task.last_checked_at = now
                task.next_execution_at = (
                    now + timedelta(minutes=task.check_interval)
            )

                self.db.commit()

            except Exception:
                self.db.rollback()
                continue