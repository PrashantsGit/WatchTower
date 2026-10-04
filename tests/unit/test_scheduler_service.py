
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from app.database.session import SessionLocal
from app.models.monitoring_task import MonitoringTask
from app.scheduler.service import SchedulerService


def create_task(
    db,
    *,
    user_id=41,
    is_active=True,
    next_execution_at=None,
):
    task = MonitoringTask(
        user_id=user_id,
        name="Scheduler Test Task",
        description="Testing scheduler",
        target_url="https://example.com",
        check_interval=60,
        is_active=is_active,
        next_execution_at=next_execution_at,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def cleanup_tasks(db, *tasks):
    for task in tasks:
        if task is not None:
            db.delete(task)

    db.commit()


def make_scheduler(db, engine, due_tasks):
    """Create a scheduler isolated from unrelated database tasks."""
    scheduler = SchedulerService(db=db, engine=engine)
    scheduler.repository.list_due_active_tasks = Mock(
        return_value=due_tasks
    )
    return scheduler


def test_scheduler_executes_active_due_task():
    db = SessionLocal()
    task = None

    try:
        now = datetime.now(timezone.utc)
        task = create_task(
            db,
            next_execution_at=now - timedelta(minutes=1),
        )
        engine = Mock()

        scheduler = make_scheduler(db, engine, [task])
        scheduler.run_pending()

        engine.execute.assert_called_once_with(
            task_id=task.id,
            user_id=task.user_id,
        )

    finally:
        cleanup_tasks(db, task)
        db.close()


def test_scheduler_does_not_execute_future_task():
    db = SessionLocal()
    task = None

    try:
        now = datetime.now(timezone.utc)
        task = create_task(
            db,
            next_execution_at=now + timedelta(minutes=5),
        )
        engine = Mock()

        # No eligible tasks should be returned for this test.
        scheduler = make_scheduler(db, engine, [])
        scheduler.run_pending()

        engine.execute.assert_not_called()

    finally:
        cleanup_tasks(db, task)
        db.close()


def test_scheduler_does_not_execute_inactive_task():
    db = SessionLocal()
    task = None

    try:
        now = datetime.now(timezone.utc)
        task = create_task(
            db,
            is_active=False,
            next_execution_at=now - timedelta(minutes=1),
        )
        engine = Mock()

        # No eligible tasks should be returned for this test.
        scheduler = make_scheduler(db, engine, [])
        scheduler.run_pending()

        engine.execute.assert_not_called()

    finally:
        cleanup_tasks(db, task)
        db.close()


def test_scheduler_executes_all_due_tasks():
    db = SessionLocal()
    task_one = None
    task_two = None

    try:
        now = datetime.now(timezone.utc)

        task_one = create_task(
            db,
            next_execution_at=now - timedelta(minutes=2),
        )
        task_two = create_task(
            db,
            next_execution_at=now - timedelta(minutes=1),
        )

        engine = Mock()
        scheduler = make_scheduler(
            db,
            engine,
            [task_one, task_two],
        )
        scheduler.run_pending()

        assert engine.execute.call_count == 2
        engine.execute.assert_any_call(
            task_id=task_one.id,
            user_id=task_one.user_id,
        )
        engine.execute.assert_any_call(
            task_id=task_two.id,
            user_id=task_two.user_id,
        )

    finally:
        cleanup_tasks(db, task_one, task_two)
        db.close()


def test_scheduler_continues_when_one_task_fails():
    db = SessionLocal()
    task_one = None
    task_two = None

    try:
        now = datetime.now(timezone.utc)

        task_one = create_task(
            db,
            next_execution_at=now - timedelta(minutes=2),
        )
        task_two = create_task(
            db,
            next_execution_at=now - timedelta(minutes=1),
        )

        engine = Mock()

        def execute(*, task_id, user_id):
            if task_id == task_one.id:
                raise Exception("Monitoring execution failed")

        engine.execute.side_effect = execute

        scheduler = make_scheduler(
            db,
            engine,
            [task_one, task_two],
        )
        scheduler.run_pending()

        assert engine.execute.call_count == 2
        engine.execute.assert_any_call(
            task_id=task_one.id,
            user_id=task_one.user_id,
        )
        engine.execute.assert_any_call(
            task_id=task_two.id,
            user_id=task_two.user_id,
        )

    finally:
        cleanup_tasks(db, task_one, task_two)
        db.close()


def test_scheduler_updates_execution_times_after_success():
    db = SessionLocal()
    task = None

    try:
        now = datetime.now(timezone.utc)
        task = create_task(
            db,
            next_execution_at=now - timedelta(minutes=1),
        )
        engine = Mock()

        scheduler = make_scheduler(db, engine, [task])
        scheduler.run_pending()

        db.refresh(task)

        assert task.last_checked_at is not None
        assert task.next_execution_at is not None
        assert task.next_execution_at > task.last_checked_at

        expected_next_execution = (
            task.last_checked_at
            + timedelta(minutes=task.check_interval)
        )
        assert task.next_execution_at == expected_next_execution

    finally:
        cleanup_tasks(db, task)
        db.close()


def test_scheduler_does_not_update_failed_task_schedule():
    db = SessionLocal()
    task = None

    try:
        now = datetime.now(timezone.utc)
        original_next_execution = now - timedelta(minutes=1)

        task = create_task(
            db,
            next_execution_at=original_next_execution,
        )
        engine = Mock()
        engine.execute.side_effect = Exception(
            "Monitoring execution failed"
        )

        scheduler = make_scheduler(db, engine, [task])
        scheduler.run_pending()

        db.refresh(task)

        assert task.last_checked_at is None
        assert task.next_execution_at == original_next_execution

    finally:
        cleanup_tasks(db, task)
        db.close()


def test_scheduler_failure_does_not_prevent_other_task_from_rescheduling():
    db = SessionLocal()
    task_one = None
    task_two = None

    try:
        now = datetime.now(timezone.utc)

        task_one = create_task(
            db,
            next_execution_at=now - timedelta(minutes=2),
        )
        task_two = create_task(
            db,
            next_execution_at=now - timedelta(minutes=1),
        )

        engine = Mock()

        def execute(*, task_id, user_id):
            if task_id == task_one.id:
                raise Exception("Monitoring execution failed")

        engine.execute.side_effect = execute

        scheduler = make_scheduler(
            db,
            engine,
            [task_one, task_two],
        )
        scheduler.run_pending()

        db.refresh(task_one)
        db.refresh(task_two)

        assert task_one.last_checked_at is None
        assert task_one.next_execution_at <= now

        assert task_two.last_checked_at is not None
        assert task_two.next_execution_at is not None
        assert task_two.next_execution_at > task_two.last_checked_at

    finally:
        cleanup_tasks(db, task_one, task_two)
        db.close()
