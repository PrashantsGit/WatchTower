import pytest
from datetime import datetime, timedelta, timezone

from app.core.exceptions import ResourceNotFoundError
from app.database.session import SessionLocal
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.services.monitoring_snapshot_service import (
    MonitoringSnapshotService,
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
        name="Snapshot Service Test",
        description="Testing snapshot service",
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
    service = MonitoringSnapshotService(db)

    snapshot = service.create_snapshot(
        task_id=task.id,
        user_id=41,
        snapshot_data={
            "price": "45000",
        },
        content_hash="service-hash-1",
        execution_status="SUCCESS",
        response_time_ms=300,
    )

    assert snapshot.id is not None
    assert snapshot.task_id == task.id
    assert snapshot.snapshot_data == {
        "price": "45000",
    }
    assert snapshot.content_hash == "service-hash-1"
    assert snapshot.execution_status == "SUCCESS"
    assert snapshot.response_time_ms == 300


def test_get_snapshot_returns_owned_snapshot(db, task):
    snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "availability": "IN_STOCK",
        },
        content_hash="service-hash-2",
        execution_status="SUCCESS",
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    service = MonitoringSnapshotService(db)

    found = service.get_snapshot(
        snapshot_id=snapshot.id,
        task_id=task.id,
        user_id=41,
    )

    assert found.id == snapshot.id
    assert found.task_id == task.id


def test_get_snapshot_rejects_snapshot_from_other_task(
    db,
    task,
):
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

    snapshot = MonitoringSnapshot(
        task_id=other_task.id,
        snapshot_data={
            "price": "50000",
        },
        content_hash="service-hash-3",
        execution_status="SUCCESS",
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    service = MonitoringSnapshotService(db)

    try:
        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring snapshot not found",
        ):
            service.get_snapshot(
                snapshot_id=snapshot.id,
                task_id=task.id,
                user_id=41,
            )

    finally:
        db.delete(snapshot)
        db.delete(other_task)
        db.commit()


def test_get_snapshot_rejects_other_user(
    db,
    task,
):
    snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "45000",
        },
        content_hash="service-hash-4",
        execution_status="SUCCESS",
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    service = MonitoringSnapshotService(db)

    with pytest.raises(
        ResourceNotFoundError,
        match="Monitoring task not found",
    ):
        service.get_snapshot(
            snapshot_id=snapshot.id,
            task_id=task.id,
            user_id=999999,
        )


def test_list_snapshots_returns_task_snapshots(
    db,
    task,
):
    snapshot_1 = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "50000",
        },
        content_hash="service-hash-5",
        execution_status="SUCCESS",
    )

    snapshot_2 = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "45000",
        },
        content_hash="service-hash-6",
        execution_status="SUCCESS",
    )

    db.add_all([
        snapshot_1,
        snapshot_2,
    ])
    db.commit()

    service = MonitoringSnapshotService(db)

    snapshots = service.list_snapshots(
        task_id=task.id,
        user_id=41,
    )

    snapshot_ids = {
        snapshot.id
        for snapshot in snapshots
    }

    assert snapshot_1.id in snapshot_ids
    assert snapshot_2.id in snapshot_ids


def test_list_snapshots_rejects_other_user(
    db,
    task,
):
    service = MonitoringSnapshotService(db)

    with pytest.raises(
        ResourceNotFoundError,
        match="Monitoring task not found",
    ):
        service.list_snapshots(
            task_id=task.id,
            user_id=999999,
        )


def test_get_latest_successful_snapshot_returns_latest_successful_snapshot(
    db,
    task,
):
    service = MonitoringSnapshotService(db)

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

    result = service.get_latest_successful_snapshot(
        task_id=task.id,
        user_id=41,
    )

    assert result is not None
    assert result.id == latest_success.id
    assert result.snapshot_data == {
        "price": "45000",
    }
    assert result.execution_status == "SUCCESS"


def test_get_latest_successful_snapshot_ignores_failed_snapshots(
    db,
    task,
):
    service = MonitoringSnapshotService(db)

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

    result = service.get_latest_successful_snapshot(
        task_id=task.id,
        user_id=41,
    )

    assert result is not None
    assert result.id == successful_snapshot.id
    assert result.execution_status == "SUCCESS"


def test_get_latest_successful_snapshot_returns_none_when_no_successful_snapshot(
    db,
    task,
):
    service = MonitoringSnapshotService(db)

    failed_snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={},
        content_hash="failed-snapshot-hash",
        execution_status="FAILED",
        captured_at=datetime.now(timezone.utc),
    )

    db.add(failed_snapshot)
    db.commit()

    result = service.get_latest_successful_snapshot(
        task_id=task.id,
        user_id=41,
    )

    assert result is None


def test_get_latest_successful_snapshot_rejects_other_user(
    db,
    task,
):
    service = MonitoringSnapshotService(db)

    with pytest.raises(
        ResourceNotFoundError,
        match="Monitoring task not found",
    ):
        service.get_latest_successful_snapshot(
            task_id=task.id,
            user_id=999999,
        )