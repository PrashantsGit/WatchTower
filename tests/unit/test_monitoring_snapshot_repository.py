import pytest

from app.database.session import SessionLocal
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.repositories.monitoring_snapshot_repository import (
    MonitoringSnapshotRepository,
)


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def task(db):
    monitoring_task = MonitoringTask(
        user_id=41,
        name="Snapshot Repository Test",
        description="Testing snapshot repository",
        target_url="https://example.com",
        check_interval=60,
        is_active=True,
    )

    db.add(monitoring_task)
    db.commit()
    db.refresh(monitoring_task)

    try:
        yield monitoring_task

    finally:
        db.query(MonitoringSnapshot).filter(
            MonitoringSnapshot.task_id == monitoring_task.id
        ).delete(
            synchronize_session=False
        )

        db.delete(monitoring_task)
        db.commit()


def test_create_snapshot(db, task):
    repository = MonitoringSnapshotRepository(db)

    snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "45000",
        },
        content_hash="test-hash-1",
        execution_status="SUCCESS",
        response_time_ms=250,
    )

    created = repository.create(snapshot)

    assert created.id is not None
    assert created.task_id == task.id
    assert created.snapshot_data == {
        "price": "45000",
    }
    assert created.content_hash == "test-hash-1"
    assert created.execution_status == "SUCCESS"
    assert created.response_time_ms == 250


def test_find_by_id_returns_snapshot(db, task):
    repository = MonitoringSnapshotRepository(db)

    snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "availability": "IN_STOCK",
        },
        content_hash="test-hash-2",
        execution_status="SUCCESS",
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    found = repository.find_by_id(
        snapshot.id
    )

    assert found is not None
    assert found.id == snapshot.id
    assert found.task_id == task.id


def test_find_by_id_returns_none_for_missing_snapshot(
    db,
):
    repository = MonitoringSnapshotRepository(db)

    found = repository.find_by_id(
        999999
    )

    assert found is None


def test_list_by_task_returns_snapshots(
    db,
    task,
):
    repository = MonitoringSnapshotRepository(db)

    snapshot_1 = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "50000",
        },
        content_hash="test-hash-3",
        execution_status="SUCCESS",
    )

    snapshot_2 = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "45000",
        },
        content_hash="test-hash-4",
        execution_status="SUCCESS",
    )

    db.add_all([
        snapshot_1,
        snapshot_2,
    ])
    db.commit()

    snapshots = repository.list_by_task(
        task.id
    )

    snapshot_ids = {
        snapshot.id
        for snapshot in snapshots
    }

    assert snapshot_1.id in snapshot_ids
    assert snapshot_2.id in snapshot_ids