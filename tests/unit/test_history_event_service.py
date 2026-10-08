import pytest

from app.core.exceptions import ResourceNotFoundError
from app.database.session import SessionLocal
from app.models.history_event import HistoryEvent
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.models.user import User
from app.services.history_event_service import HistoryEventService


def create_test_data(db):
    user = User(
        full_name="History Event Test User",
        email="history-event-test@example.com",
        password_hash="test-password",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    task = MonitoringTask(
        user_id=user.id,
        name="History Event Test",
        description="Testing history events",
        target_url="https://example.com",
        check_interval=60,
        is_active=True,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "45000",
        },
        content_hash="test-hash",
        execution_status="SUCCESS",
        response_time_ms=250,
    )

    db.add(rule)
    db.add(snapshot)
    db.commit()

    db.refresh(rule)
    db.refresh(snapshot)

    return user, task, rule, snapshot


def test_create_history_event():
    db = SessionLocal()

    user = None

    try:
        user, task, rule, snapshot = create_test_data(db)

        service = HistoryEventService(db)

        event = service.create_event(
            task_id=task.id,
            rule_id=rule.id,
            snapshot_id=snapshot.id,
            event_type="PRICE_DROP",
            previous_value="55000",
            current_value="45000",
            event_message="Price dropped below target.",
        )

        assert event.id is not None
        assert event.task_id == task.id
        assert event.rule_id == rule.id
        assert event.snapshot_id == snapshot.id
        assert event.event_type == "PRICE_DROP"
        assert event.previous_value == "55000"
        assert event.current_value == "45000"
        assert (
            event.event_message
            == "Price dropped below target."
        )

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_get_history_event():
    db = SessionLocal()

    user = None

    try:
        user, task, rule, snapshot = create_test_data(db)

        service = HistoryEventService(db)

        event = service.create_event(
            task_id=task.id,
            rule_id=rule.id,
            snapshot_id=snapshot.id,
            event_type="STOCK_AVAILABLE",
            previous_value="OUT_OF_STOCK",
            current_value="IN_STOCK",
            event_message="Product is now available.",
        )

        found = service.get_event(
            event_id=event.id,
            task_id=task.id,
        )

        assert found.id == event.id
        assert found.task_id == task.id
        assert found.rule_id == rule.id
        assert found.snapshot_id == snapshot.id

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_get_history_event_rejects_wrong_task():
    db = SessionLocal()

    user = None

    try:
        user, task, rule, snapshot = create_test_data(db)

        service = HistoryEventService(db)

        event = service.create_event(
            task_id=task.id,
            rule_id=rule.id,
            snapshot_id=snapshot.id,
            event_type="KEYWORD_DETECTED",
            previous_value=None,
            current_value="sale",
            event_message="Keyword detected.",
        )

        with pytest.raises(
            ResourceNotFoundError,
            match="History event not found",
        ):
            service.get_event(
                event_id=event.id,
                task_id=999999,
            )

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()

def test_list_history_events_for_user():
    db = SessionLocal()

    user = None

    try:
        user, task, rule, snapshot = create_test_data(db)

        service = HistoryEventService(db)

        event = service.create_event(
            task_id=task.id,
            rule_id=rule.id,
            snapshot_id=snapshot.id,
            event_type="PRICE_DROP",
            previous_value="50000",
            current_value="45000",
            event_message="Price dropped.",
        )

        events = service.list_events_for_user(
            user_id=user.id,
            limit=20,
            offset=0,
        )

        event_ids = [item.id for item in events]

        assert event.id in event_ids

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_list_history_events_for_task():
    db = SessionLocal()

    user = None

    try:
        user, task, rule, snapshot = create_test_data(db)

        service = HistoryEventService(db)

        event = service.create_event(
            task_id=task.id,
            rule_id=rule.id,
            snapshot_id=snapshot.id,
            event_type="STOCK_AVAILABLE",
            previous_value="OUT_OF_STOCK",
            current_value="IN_STOCK",
            event_message="Product is available.",
        )

        events = service.list_events_for_task(
            task_id=task.id,
            user_id=user.id,
            limit=20,
            offset=0,
        )

        assert len(events) == 1
        assert events[0].id == event.id

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_list_history_events_for_task_rejects_other_user():
    db = SessionLocal()

    user = None

    try:
        user, task, rule, snapshot = create_test_data(db)

        service = HistoryEventService(db)

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.list_events_for_task(
                task_id=task.id,
                user_id=999999,
                limit=20,
                offset=0,
            )

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_list_history_events_for_task_rejects_missing_task():
    db = SessionLocal()

    try:
        service = HistoryEventService(db)

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.list_events_for_task(
                task_id=999999,
                user_id=999999,
                limit=20,
                offset=0,
            )

    finally:
        db.close()