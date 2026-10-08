from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.database.session import SessionLocal
from app.models.history_event import HistoryEvent
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.models.user import User
from app.repositories.history_event_repository import (
    HistoryEventRepository,
)


def create_test_data(db):
    user_a = User(
        full_name="History Repository User A",
        email=f"history-repository-a-{uuid4()}@example.com",
        password_hash="test-password",
    )

    user_b = User(
        full_name="History Repository User B",
        email=f"history-repository-b-{uuid4()}@example.com",
        password_hash="test-password",
    )

    db.add_all([user_a, user_b])
    db.commit()

    db.refresh(user_a)
    db.refresh(user_b)

    task_a = MonitoringTask(
        user_id=user_a.id,
        name="User A Task",
        description="History repository test",
        target_url="https://example.com/a",
        check_interval=60,
        is_active=True,
    )

    task_b = MonitoringTask(
        user_id=user_b.id,
        name="User B Task",
        description="History repository test",
        target_url="https://example.com/b",
        check_interval=60,
        is_active=True,
    )

    db.add_all([task_a, task_b])
    db.commit()

    db.refresh(task_a)
    db.refresh(task_b)

    rule_a = MonitoringRule(
        task_id=task_a.id,
        rule_type="KEYWORD",
        operator="contains",
        target_value="Example",
        is_enabled=True,
    )

    rule_b = MonitoringRule(
        task_id=task_b.id,
        rule_type="KEYWORD",
        operator="contains",
        target_value="Example",
        is_enabled=True,
    )

    snapshot_a = MonitoringSnapshot(
        task_id=task_a.id,
        snapshot_data={"content": "Example A"},
        content_hash="repository-test-hash-a",
        execution_status="SUCCESS",
        response_time_ms=100,
    )

    snapshot_b = MonitoringSnapshot(
        task_id=task_b.id,
        snapshot_data={"content": "Example B"},
        content_hash="repository-test-hash-b",
        execution_status="SUCCESS",
        response_time_ms=100,
    )

    db.add_all([
        rule_a,
        rule_b,
        snapshot_a,
        snapshot_b,
    ])
    db.commit()

    db.refresh(rule_a)
    db.refresh(rule_b)
    db.refresh(snapshot_a)
    db.refresh(snapshot_b)

    return (
        user_a,
        user_b,
        task_a,
        task_b,
        rule_a,
        rule_b,
        snapshot_a,
        snapshot_b,
    )


def create_event(
    db,
    task,
    rule,
    snapshot,
    event_type,
    detected_at=None,
):
    event = HistoryEvent(
        task_id=task.id,
        rule_id=rule.id,
        snapshot_id=snapshot.id,
        event_type=event_type,
        previous_value="old",
        current_value="new",
        event_message=f"{event_type} detected.",
    )

    if detected_at is not None:
        event.detected_at = detected_at

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def test_history_event_repository_lists_events_for_user():
    db = SessionLocal()

    try:
        (
            user_a,
            user_b,
            task_a,
            task_b,
            rule_a,
            rule_b,
            snapshot_a,
            snapshot_b,
        ) = create_test_data(db)

        own_event = create_event(
            db,
            task_a,
            rule_a,
            snapshot_a,
            "PRICE_DROP",
        )

        other_event = create_event(
            db,
            task_b,
            rule_b,
            snapshot_b,
            "STOCK_AVAILABLE",
        )

        repository = HistoryEventRepository(db)

        events = repository.list_for_user(
            user_id=user_a.id,
            limit=20,
            offset=0,
        )

        event_ids = [event.id for event in events]

        assert own_event.id in event_ids
        assert other_event.id not in event_ids

    finally:
        db.rollback()
        db.close()


def test_history_event_repository_lists_task_history_for_owner():
    db = SessionLocal()

    try:
        (
            user_a,
            user_b,
            task_a,
            task_b,
            rule_a,
            rule_b,
            snapshot_a,
            snapshot_b,
        ) = create_test_data(db)

        event_a = create_event(
            db,
            task_a,
            rule_a,
            snapshot_a,
            "PRICE_DROP",
        )

        event_b = create_event(
            db,
            task_b,
            rule_b,
            snapshot_b,
            "STOCK_AVAILABLE",
        )

        repository = HistoryEventRepository(db)

        events = repository.list_by_task_for_user(
            task_id=task_a.id,
            user_id=user_a.id,
            limit=20,
            offset=0,
        )

        event_ids = [event.id for event in events]

        assert event_a.id in event_ids
        assert event_b.id not in event_ids

    finally:
        db.rollback()
        db.close()


def test_history_event_repository_rejects_other_user_task():
    db = SessionLocal()

    try:
        (
            user_a,
            user_b,
            task_a,
            task_b,
            rule_a,
            rule_b,
            snapshot_a,
            snapshot_b,
        ) = create_test_data(db)

        create_event(
            db,
            task_a,
            rule_a,
            snapshot_a,
            "PRICE_DROP",
        )

        repository = HistoryEventRepository(db)

        events = repository.list_by_task_for_user(
            task_id=task_a.id,
            user_id=user_b.id,
            limit=20,
            offset=0,
        )

        assert events == []

    finally:
        db.rollback()
        db.close()


def test_history_event_repository_supports_pagination():
    db = SessionLocal()

    try:
        (
            user_a,
            _user_b,
            task_a,
            _task_b,
            rule_a,
            _rule_b,
            snapshot_a,
            _snapshot_b,
        ) = create_test_data(db)

        events = []

        for index in range(5):
            events.append(
                create_event(
                    db,
                    task_a,
                    rule_a,
                    snapshot_a,
                    f"EVENT_{index}",
                )
            )

        repository = HistoryEventRepository(db)

        first_page = repository.list_for_user(
            user_id=user_a.id,
            limit=2,
            offset=0,
        )

        second_page = repository.list_for_user(
            user_id=user_a.id,
            limit=2,
            offset=2,
        )

        assert len(first_page) == 2
        assert len(second_page) == 2

        first_ids = {event.id for event in first_page}
        second_ids = {event.id for event in second_page}

        assert first_ids.isdisjoint(second_ids)

    finally:
        db.rollback()
        db.close()


def test_history_event_repository_orders_newest_first():
    db = SessionLocal()

    try:
        (
            user_a,
            _user_b,
            task_a,
            _task_b,
            rule_a,
            _rule_b,
            snapshot_a,
            _snapshot_b,
        ) = create_test_data(db)

        now = datetime.now(timezone.utc)

        older = create_event(
            db,
            task_a,
            rule_a,
            snapshot_a,
            "OLDER",
            detected_at=now - timedelta(minutes=10),
        )

        newer = create_event(
            db,
            task_a,
            rule_a,
            snapshot_a,
            "NEWER",
            detected_at=now,
        )

        repository = HistoryEventRepository(db)

        events = repository.list_for_user(
            user_id=user_a.id,
            limit=20,
            offset=0,
        )

        relevant_events = [
            event
            for event in events
            if event.id in {older.id, newer.id}
        ]

        assert relevant_events[0].id == newer.id
        assert relevant_events[1].id == older.id

    finally:
        db.rollback()
        db.close()