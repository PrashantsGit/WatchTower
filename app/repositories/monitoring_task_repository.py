from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monitoring_task import MonitoringTask


class MonitoringTaskRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, task: MonitoringTask) -> MonitoringTask:
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def find_by_id_for_user(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringTask | None:
        statement = select(MonitoringTask).where(
            MonitoringTask.id == task_id,
            MonitoringTask.user_id == user_id,
        )

        return self.db.scalar(statement)

    def list_by_user(
        self,
        user_id: int,
    ) -> list[MonitoringTask]:
        statement = (
            select(MonitoringTask)
            .where(MonitoringTask.user_id == user_id)
            .order_by(MonitoringTask.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, task: MonitoringTask) -> MonitoringTask:
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task: MonitoringTask) -> None:
        self.db.delete(task)
        self.db.flush()

    def pause(self, task: MonitoringTask) -> MonitoringTask:
        task.is_active = False
        self.db.flush()
        self.db.refresh(task)
        return task

    def resume(self, task: MonitoringTask) -> MonitoringTask:
        task.is_active = True
        self.db.flush()
        self.db.refresh(task)
        return task