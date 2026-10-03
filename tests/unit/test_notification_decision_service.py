import pytest

from app.core.exceptions import ResourceNotFoundError
from app.models.history_event import HistoryEvent
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.models.notification_preference import (
    NotificationPreference,
)
from app.models.user import User
from app.services.notification_decision_service import (
    NotificationDecisionService,
)
from app.database.session import SessionLocal


def create_test_data(db):
    user = User(
        full_name="Notification Decision User",
        email="notification-decision@example.com",
        password_hash="test-password-hash",
    )

    db.add(user)
    db.flush()

    preference = NotificationPreference(
        user_id=user.id,
        email_enabled=True,
        browser_push_enabled=True,
        notify_on_price_change=True,
        notify_on_stock_change=True,
    )

    db.add(preference)
    db.flush()

    task = MonitoringTask(
        user_id=user.id,
        name="Notification Decision Task",
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
        content_hash="notification-decision-hash",
        execution_status="SUCCESS",
    )

    db.add(snapshot)
    db.flush()

    event = HistoryEvent(
        task_id=task.id,
        rule_id=rule.id,
        snapshot_id=snapshot.id,
        event_type="PRICE_DROP",
        previous_value="120",
        current_value="90",
        event_message="Price condition triggered.",
    )

    db.add(event)
    db.commit()

    db.refresh(user)
    db.refresh(preference)
    db.refresh(task)
    db.refresh(rule)
    db.refresh(snapshot)
    db.refresh(event)

    return (
        user,
        preference,
        task,
        rule,
        snapshot,
        event,
    )


def test_price_event_creates_email_and_browser_notifications():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        channels = {
            notification.notification_channel
            for notification in notifications
        }

        assert channels == {
            "EMAIL",
            "BROWSER_PUSH",
        }

        assert len(notifications) == 2

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_price_event_creates_only_email_when_browser_push_disabled():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        preference.browser_push_enabled = False
        db.commit()

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        assert len(notifications) == 1
        assert (
            notifications[0].notification_channel
            == "EMAIL"
        )

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_price_event_creates_only_browser_push_when_email_disabled():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        preference.email_enabled = False
        db.commit()

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        assert len(notifications) == 1
        assert (
            notifications[0].notification_channel
            == "BROWSER_PUSH"
        )

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_price_event_creates_no_notification_when_price_notifications_disabled():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        preference.notify_on_price_change = False
        db.commit()

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        assert notifications == []

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


@pytest.mark.parametrize(
    "event_type",
    [
        "STOCK_AVAILABLE",
        "STOCK_UNAVAILABLE",
        "AVAILABILITY_CHANGED",
    ],
)
def test_stock_events_create_notifications_when_enabled(
    event_type,
):
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        event.event_type = event_type
        db.commit()

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        channels = {
            notification.notification_channel
            for notification in notifications
        }

        assert channels == {
            "EMAIL",
            "BROWSER_PUSH",
        }

        assert len(notifications) == 2

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_stock_event_creates_no_notification_when_stock_notifications_disabled():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        event.event_type = "STOCK_AVAILABLE"
        preference.notify_on_stock_change = False
        db.commit()

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        assert notifications == []

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_unknown_event_type_creates_no_notification():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        event.event_type = "KEYWORD_DETECTED"
        db.commit()

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        assert notifications == []

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_no_channels_enabled_creates_no_notifications():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        preference.email_enabled = False
        preference.browser_push_enabled = False
        db.commit()

        service = NotificationDecisionService(db)

        notifications = (
            service.create_notifications_for_event(
                event=event,
                user_id=user.id,
            )
        )

        assert notifications == []

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_notification_decision_enforces_user_preferences_ownership():
    db = SessionLocal()

    try:
        (
            user,
            preference,
            task,
            rule,
            snapshot,
            event,
        ) = create_test_data(db)

        service = NotificationDecisionService(db)

        with pytest.raises(ResourceNotFoundError):
            service.create_notifications_for_event(
                event=event,
                user_id=999999999,
            )

    finally:
        db.query(User).filter(
            User.email
            == "notification-decision@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()