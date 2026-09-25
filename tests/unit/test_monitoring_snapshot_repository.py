import pytest
from datetime import datetime, timedelta, timezone

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


def test_list_by_task_returns_empty_list_for_unknown_task(
    db,
):
    repository = MonitoringSnapshotRepository(db)

    snapshots = repository.list_by_task(
        999999
    )

    assert snapshots == []


def test_list_by_task_does_not_return_other_task_snapshots(
    db,
    task,
):
    repository = MonitoringSnapshotRepository(db)

    other_task = MonitoringTask(
        user_id=41,
        name="Other Snapshot Task",
        description="Another task",
        target_url="https://example.org",
        check_interval=60,
        is_active=True,
    )

    db.add(other_task)
    db.commit()
    db.refresh(other_task)

    try:
        snapshot_1 = MonitoringSnapshot(
            task_id=task.id,
            snapshot_data={
                "price": "50000",
            },
            content_hash="test-hash-5",
            execution_status="SUCCESS",
        )

        snapshot_2 = MonitoringSnapshot(
            task_id=other_task.id,
            snapshot_data={
                "price": "45000",
            },
            content_hash="test-hash-6",
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

        assert len(snapshots) == 1
        assert snapshots[0].task_id == task.id

    finally:
        db.query(MonitoringSnapshot).filter(
            MonitoringSnapshot.task_id == other_task.id
        ).delete(
            synchronize_session=False
        )

        db.delete(other_task)
        db.commit()


def test_get_latest_successful_by_task_returns_latest_successful_snapshot(
    db,
    task,
):
    repository = MonitoringSnapshotRepository(db)

    now = datetime.now(timezone.utc)

    older_success = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "50000",
        },
        content_hash="old-success",
        execution_status="SUCCESS",
        captured_at=now - timedelta(minutes=2),
    )

    latest_success = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "45000",
        },
        content_hash="latest-success",
        execution_status="SUCCESS",
        captured_at=now - timedelta(minutes=1),
    )

    db.add_all([
        older_success,
        latest_success,
    ])
    db.commit()

    result = repository.get_latest_successful_by_task(
        task.id
    )

    assert result is not None
    assert result.id == latest_success.id
    assert result.snapshot_data == {
        "price": "45000",
    }
    assert result.execution_status == "SUCCESS"


def test_get_latest_successful_by_task_ignores_failed_snapshots(
    db,
    task,
):
    repository = MonitoringSnapshotRepository(db)

    now = datetime.now(timezone.utc)

    successful_snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "50000",
        },
        content_hash="success",
        execution_status="SUCCESS",
        captured_at=now - timedelta(minutes=2),
    )

    failed_snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={},
        content_hash="failed-snapshot-hash",
        execution_status="FAILED",
        captured_at=now - timedelta(minutes=1),
    )

    db.add_all([
        successful_snapshot,
        failed_snapshot,
    ])
    db.commit()

    result = repository.get_latest_successful_by_task(
        task.id
    )

    assert result is not None
    assert result.id == successful_snapshot.id
    assert result.execution_status == "SUCCESS"


def test_get_latest_successful_by_task_returns_none_when_no_successful_snapshot(
    db,
    task,
):
    repository = MonitoringSnapshotRepository(db)

    failed_snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={},
        content_hash="failed-snapshot-hash",
        execution_status="FAILED",
        captured_at=datetime.now(timezone.utc),
    )

    db.add(failed_snapshot)
    db.commit()

    result = repository.get_latest_successful_by_task(
        task.id
    )

    assert result is None


def test_get_latest_successful_by_task_returns_none_for_unknown_task(
    db,
):
    repository = MonitoringSnapshotRepository(db)

    result = repository.get_latest_successful_by_task(
        999999
    )

    assert result is None