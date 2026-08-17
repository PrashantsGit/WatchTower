from sqlalchemy.orm import Session

from app.models.monitoring_task import MonitoringTask
from app.repositories.monitoring_task_repository import MonitoringTaskRepository
from app.core.exceptions import ResourceNotFoundError

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

    def get_task(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringTask:
        task = self.task_repository.find_by_id_for_user(
        task_id=task_id,
        user_id=user_id,
        )

        if task is None:
            raise ResourceNotFoundError("Monitoring task not found.")

        return task

    def update_task(
        self,
        task_id: int,
        user_id: int,
        name: str,
        description: str | None,
        target_url: str,
        check_interval: int,
    ) -> MonitoringTask:
        task = self.task_repository.find_by_id_for_user(
            task_id=task_id,
            user_id=user_id,
        )

        if task is None:
            raise ResourceNotFoundError("Monitoring task not found.")

        task.name = name.strip()
        task.description = description.strip() if description else None
        task.target_url = target_url.strip()
        task.check_interval = check_interval

        try:
            task = self.task_repository.update(task)
            self.db.commit()
            self.db.refresh(task)
            return task

        except Exception:
            self.db.rollback()
            raise

    def delete_task(
        self,
        task_id: int,
        user_id: int,
    ) -> None:
        task = self.task_repository.find_by_id_for_user(
            task_id=task_id,
            user_id=user_id,
        )

        if task is None:
            raise ResourceNotFoundError("Monitoring task not found.")

        try:
            self.task_repository.delete(task)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    def pause_task(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringTask:
        task = self.task_repository.find_by_id_for_user(
            task_id=task_id,
            user_id=user_id,
        )

        if task is None:
            raise ResourceNotFoundError("Monitoring task not found.")

        try:
            task = self.task_repository.pause(task)
            self.db.commit()
            self.db.refresh(task)
            return task

        except Exception:
            self.db.rollback()
            raise


    def resume_task(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringTask:
        task = self.task_repository.find_by_id_for_user(
            task_id=task_id,
            user_id=user_id,
        )

        if task is None:
            raise ResourceNotFoundError("Monitoring task not found.")

        try:
            task = self.task_repository.resume(task)
            self.db.commit()
            self.db.refresh(task)
            return task

        except Exception:
            self.db.rollback()
            raise