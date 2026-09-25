import pytest

from app.core.exceptions import ResourceNotFoundError
from app.models.history_event import HistoryEvent
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.models.notification import Notification
from app.models.user import User
from app.services.history_event_service import HistoryEventService
from app.services.notification_service import NotificationService
from app.database.session import SessionLocal


def create_test_data(db):
    user = User(
        full_name="Notification Service User",
        email="notification-service@example.com",
        password_hash="test-password-hash",
    )

    db.add(user)
    db.flush()

    task = MonitoringTask(
        user_id=user.id,
        name="Notification Test Task",
        target_url="https://example.com",
        check_interval=60,
        is_active=True,
    )

    db.add(task)
    db.flush()

    rule = MonitoringRule(
        task_id=task.id,
        rule_type="PRICE",
        operator="LESS_THAN",
        target_value="100",
        is_enabled=True,
    )

    db.add(rule)
    db.flush()

    snapshot = MonitoringSnapshot(
        task_id=task.id,
        snapshot_data={
            "price": "120",
            "availability": "IN_STOCK",
            "text": "Example product",
        },
        content_hash="notification-test-hash",
        execution_status="SUCCESS",
    )

    db.add(snapshot)
    db.flush()

    history_event = HistoryEvent(
        task_id=task.id,
        rule_id=rule.id,
        snapshot_id=snapshot.id,
        event_type="PRICE_DROP",
        previous_value="120",
        current_value="90",
        event_message="Price condition triggered.",
    )

    db.add(history_event)
    db.commit()

    db.refresh(user)
    db.refresh(task)
    db.refresh(rule)
    db.refresh(snapshot)
    db.refresh(history_event)

    return user, task, rule, snapshot, history_event


def test_create_notification():
    db = SessionLocal()

    try:
        (
            user,
            task,
            rule,
            snapshot,
            history_event,
        ) = create_test_data(db)

        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        assert notification.id is not None
        assert (
            notification.history_event_id
            == history_event.id
        )
        assert (
            notification.notification_channel
            == "EMAIL"
        )
        assert (
            notification.notification_status
            == "PENDING"
        )
        assert notification.delivered_at is None
        assert notification.error_message is None

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_create_notification_requires_existing_history_event():
    db = SessionLocal()

    try:
        service = NotificationService(db)

        with pytest.raises(Exception):
            service.create_notification(
                history_event_id=999999999,
                notification_channel="EMAIL",
            )

    finally:
        db.close()


def test_get_notification_enforces_user_ownership():
    db = SessionLocal()

    try:
        (
            user,
            task,
            rule,
            snapshot,
            history_event,
        ) = create_test_data(db)

        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        retrieved = service.get_notification(
            notification_id=notification.id,
            user_id=user.id,
        )

        assert retrieved.id == notification.id

        with pytest.raises(ResourceNotFoundError):
            service.get_notification(
                notification_id=notification.id,
                user_id=999999999,
            )

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_list_notifications_by_history_event():
    db = SessionLocal()

    try:
        (
            user,
            task,
            rule,
            snapshot,
            history_event,
        ) = create_test_data(db)

        service = NotificationService(db)

        first = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        second = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="BROWSER_PUSH",
        )

        notifications = service.list_by_history_event(
            history_event_id=history_event.id,
            user_id=user.id,
        )

        notification_ids = {
            notification.id
            for notification in notifications
        }

        assert notification_ids == {
            first.id,
            second.id,
        }

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_mark_notification_delivered():
    db = SessionLocal()

    try:
        (
            user,
            task,
            rule,
            snapshot,
            history_event,
        ) = create_test_data(db)

        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        updated = service.mark_delivered(
            notification_id=notification.id,
            user_id=user.id,
        )

        assert (
            updated.notification_status
            == "DELIVERED"
        )
        assert updated.delivered_at is not None
        assert updated.error_message is None

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_mark_notification_failed():
    db = SessionLocal()

    try:
        (
            user,
            task,
            rule,
            snapshot,
            history_event,
        ) = create_test_data(db)

        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        updated = service.mark_failed(
            notification_id=notification.id,
            user_id=user.id,
            error_message="Email provider unavailable.",
        )

        assert (
            updated.notification_status
            == "FAILED"
        )
        assert updated.delivered_at is None
        assert (
            updated.error_message
            == "Email provider unavailable."
        )

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_mark_notification_requires_ownership():
    db = SessionLocal()

    try:
        (
            user,
            task,
            rule,
            snapshot,
            history_event,
        ) = create_test_data(db)

        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        with pytest.raises(ResourceNotFoundError):
            service.mark_delivered(
                notification_id=notification.id,
                user_id=999999999,
            )

        with pytest.raises(ResourceNotFoundError):
            service.mark_failed(
                notification_id=notification.id,
                user_id=999999999,
                error_message="Unauthorized attempt.",
            )

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()