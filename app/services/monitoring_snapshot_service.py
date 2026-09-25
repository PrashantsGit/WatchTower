from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.repositories.monitoring_snapshot_repository import (
    MonitoringSnapshotRepository,
)


class MonitoringSnapshotService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = MonitoringSnapshotRepository(db)

    def create_snapshot(
        self,
        task_id: int,
        user_id: int,
        snapshot_data: dict,
        content_hash: str,
        execution_status: str,
        response_time_ms: int | None = None,
    ) -> MonitoringSnapshot:

        task = self.db.get(
            MonitoringTask,
            task_id,
        )

        if task is None or task.user_id != user_id:
            raise ResourceNotFoundError(
                "Monitoring task not found."
            )

        snapshot = MonitoringSnapshot(
            task_id=task_id,
            snapshot_data=snapshot_data,
            content_hash=content_hash,
            execution_status=execution_status,
            response_time_ms=response_time_ms,
        )

        return self.repository.create(snapshot)

    def get_snapshot(
        self,
        snapshot_id: int,
        task_id: int,
        user_id: int,
    ) -> MonitoringSnapshot:

        task = self.db.get(
            MonitoringTask,
            task_id,
        )

        if task is None or task.user_id != user_id:
            raise ResourceNotFoundError(
                "Monitoring task not found."
            )

        snapshot = self.repository.find_by_id(
            snapshot_id
        )

        if (
            snapshot is None
            or snapshot.task_id != task_id
        ):
            raise ResourceNotFoundError(
                "Monitoring snapshot not found."
            )

        return snapshot

    def list_snapshots(
        self,
        task_id: int,
        user_id: int,
    ) -> list[MonitoringSnapshot]:

        task = self.db.get(
            MonitoringTask,
            task_id,
        )

        if task is None or task.user_id != user_id:
            raise ResourceNotFoundError(
                "Monitoring task not found."
            )

        return self.repository.list_by_task(
            task_id
        )

    def get_latest_successful_snapshot(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringSnapshot | None:

        task = self.db.get(
            MonitoringTask,
            task_id,
        )

        if task is None or task.user_id != user_id:
            raise ResourceNotFoundError(
                "Monitoring task not found."
            )

        return self.repository.get_latest_successful_by_task(
            task_id
        )