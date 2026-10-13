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

def test_list_notifications_only_returns_current_users():
    db = SessionLocal()

    try:
        first_user, _, _, _, first_event = create_test_data(db)

        second_user = User(
            full_name="Second Notification User",
            email="notification-service-second@example.com",
            password_hash="test-password-hash",
        )
        db.add(second_user)
        db.flush()

        second_task = MonitoringTask(
            user_id=second_user.id,
            name="Second User Task",
            target_url="https://example.org",
            check_interval=60,
            is_active=True,
        )
        db.add(second_task)
        db.flush()

        second_rule = MonitoringRule(
            task_id=second_task.id,
            rule_type="PRICE",
            operator="LESS_THAN",
            target_value="100",
            is_enabled=True,
        )
        db.add(second_rule)
        db.flush()

        second_snapshot = MonitoringSnapshot(
            task_id=second_task.id,
            snapshot_data={
                "price": "120",
                "availability": "IN_STOCK",
                "text": "Second example product",
            },
            content_hash="notification-second-user-hash",
            execution_status="SUCCESS",
        )
        db.add(second_snapshot)
        db.flush()

        second_event = HistoryEvent(
            task_id=second_task.id,
            rule_id=second_rule.id,
            snapshot_id=second_snapshot.id,
            event_type="PRICE_DROP",
            previous_value="120",
            current_value="90",
            event_message="Second user's price condition triggered.",
        )
        db.add(second_event)
        db.commit()

        service = NotificationService(db)

        first_notification = service.create_notification(
            history_event_id=first_event.id,
            notification_channel="EMAIL",
        )
        service.create_notification(
            history_event_id=second_event.id,
            notification_channel="EMAIL",
        )

        results = service.list_notifications(
            user_id=first_user.id,
            limit=20,
            offset=0,
        )

        assert len(results) == 1
        assert results[0].id == first_notification.id
        assert results[0].history_event.task.user_id == first_user.id

    finally:
        db.query(User).filter(
            User.email.in_([
                "notification-service@example.com",
                "notification-service-second@example.com",
            ])
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_list_notifications_supports_limit_and_offset():
    db = SessionLocal()

    try:
        user, _, _, _, history_event = create_test_data(db)
        service = NotificationService(db)

        created = [
            service.create_notification(
                history_event_id=history_event.id,
                notification_channel=channel,
            )
            for channel in ("EMAIL", "BROWSER_PUSH", "EMAIL")
        ]

        results = service.list_notifications(
            user_id=user.id,
            limit=1,
            offset=1,
        )

        assert len(results) == 1
        assert results[0].id == sorted(
            [item.id for item in created],
            reverse=True,
        )[1]

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_mark_notification_as_read_is_idempotent():
    db = SessionLocal()

    try:
        user, _, _, _, history_event = create_test_data(db)
        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        first = service.mark_as_read(
            notification_id=notification.id,
            user_id=user.id,
        )
        original_read_at = first.read_at

        assert original_read_at is not None

        second = service.mark_as_read(
            notification_id=notification.id,
            user_id=user.id,
        )

        assert second.read_at == original_read_at

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_mark_notification_as_read_requires_ownership():
    db = SessionLocal()

    try:
        user, _, _, _, history_event = create_test_data(db)
        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        with pytest.raises(ResourceNotFoundError):
            service.mark_as_read(
                notification_id=notification.id,
                user_id=999999999,
            )

        with pytest.raises(ResourceNotFoundError):
            service.mark_as_read(
                notification_id=999999999,
                user_id=user.id,
            )

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_delete_notification_preserves_history_event():
    db = SessionLocal()

    try:
        user, _, _, _, history_event = create_test_data(db)
        service = NotificationService(db)

        notification = service.create_notification(
            history_event_id=history_event.id,
            notification_channel="EMAIL",
        )

        notification_id = notification.id
        history_event_id = history_event.id

        service.delete_notification(
            notification_id=notification_id,
            user_id=user.id,
        )

        assert db.get(Notification, notification_id) is None
        assert db.get(HistoryEvent, history_event_id) is not None

        with pytest.raises(ResourceNotFoundError):
            service.delete_notification(
                notification_id=notification_id,
                user_id=user.id,
            )

    finally:
        db.query(User).filter(
            User.email == "notification-service@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()
