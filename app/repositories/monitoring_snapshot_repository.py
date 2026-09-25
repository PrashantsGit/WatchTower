from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monitoring_snapshot import MonitoringSnapshot


class MonitoringSnapshotRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        snapshot: MonitoringSnapshot,
    ) -> MonitoringSnapshot:
        self.db.add(snapshot)
        self.db.flush()
        self.db.refresh(snapshot)
        return snapshot

    def find_by_id(
        self,
        snapshot_id: int,
    ) -> MonitoringSnapshot | None:
        statement = select(
            MonitoringSnapshot
        ).where(
            MonitoringSnapshot.id == snapshot_id,
        )

        return self.db.scalar(statement)

    def list_by_task(
        self,
        task_id: int,
    ) -> list[MonitoringSnapshot]:

        statement = (
            select(MonitoringSnapshot)
            .where(
                MonitoringSnapshot.task_id == task_id,
            )
            .order_by(
                MonitoringSnapshot.captured_at.desc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_latest_successful_by_task(
        self,
        task_id: int,
    ) -> MonitoringSnapshot | None:

        statement = (
            select(MonitoringSnapshot)
            .where(
                MonitoringSnapshot.task_id == task_id,
                MonitoringSnapshot.execution_status == "SUCCESS",
            )
            .order_by(
                MonitoringSnapshot.captured_at.desc(),
            )
            .limit(1)
        )

        return self.db.scalar(statement)