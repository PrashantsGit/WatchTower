from sqlalchemy.orm import Session

from app.models.monitoring_task import MonitoringTask
from app.repositories.monitoring_task_repository import MonitoringTaskRepository


class MonitoringTaskService:

    def __init__(self, db: Session):
        self.db = db
        self.task_repository = MonitoringTaskRepository(db)

    def create_task(
        self,
        user_id: int,
        name: str,
        description: str | None,
        target_url: str,
        check_interval: int = 60,
    ) -> MonitoringTask:
        task = MonitoringTask(
            user_id=user_id,
            name=name.strip(),
            description=description.strip() if description else None,
            target_url=target_url.strip(),
            check_interval=check_interval,
            is_active=True,
        )

        try:
            task = self.task_repository.create(task)
            self.db.commit()
            self.db.refresh(task)
            return task

        except Exception:
            self.db.rollback()
            raise

    def list_tasks(
        self,
        user_id: int,
    ) -> list[MonitoringTask]:
        return self.task_repository.list_by_user(user_id)