from types import SimpleNamespace
from unittest.mock import Mock

from app.services.notification_delivery_service import (
    NotificationDeliveryService,
)


def make_notification(
    notification_id: int,
    channel: str = "EMAIL",
    user_id: int = 41,
):
    user = SimpleNamespace(
        email=f"user{user_id}@example.com",
    )

    task = SimpleNamespace(
        id=12,
        user_id=user_id,
        name="Product Watch",
        target_url="https://example.com/product",
        user=user,
    )

    event = SimpleNamespace(
        id=23,
        event_type="PRICE_DROP",
        event_message="The product price decreased.",
        previous_value="500",
        current_value="450",
        task=task,
    )

    return SimpleNamespace(
        id=notification_id,
        notification_channel=channel,
        history_event=event,
    )


def make_service(notifications, provider):
    service = NotificationDeliveryService(
        db=Mock(),
        email_provider=provider,
    )
    service.repository.list_pending = Mock(
        return_value=notifications,
    )
    service.notification_service.mark_delivered = Mock()
    service.notification_service.mark_failed = Mock()
    return service



def test_delivery_marks_email_as_delivered():
    notification = make_notification(1)
    provider = Mock()

    service = make_service([notification], provider)

    result = service.process_pending()

    provider.send.assert_called_once()
    kwargs = provider.send.call_args.kwargs

    assert kwargs["recipient_email"] == "user41@example.com"
    assert kwargs["subject"] == "WatchTower alert: Price Drop"
    assert "Product Watch" in kwargs["body"]
    assert "500" in kwargs["body"]
    assert "450" in kwargs["body"]

    service.notification_service.mark_delivered.assert_called_once_with(
        notification_id=1,
        user_id=41,
    )
    service.notification_service.mark_failed.assert_not_called()

    assert result == {
        "processed": 1,
        "delivered": 1,
        "failed": 0,
        "skipped": 0,
    }



def test_delivery_marks_failed_email_and_continues():
    first = make_notification(1, user_id=41)
    second = make_notification(2, user_id=42)

    provider = Mock()
    provider.send.side_effect = [
        RuntimeError("SMTP server unavailable"),
        None,
    ]

    service = make_service(
        [first, second],
        provider,
    )

    result = service.process_pending()

    assert provider.send.call_count == 2

    service.notification_service.mark_failed.assert_called_once()
    failed_kwargs = (
        service.notification_service.mark_failed.call_args.kwargs
    )

    assert failed_kwargs["notification_id"] == 1
    assert failed_kwargs["user_id"] == 41
    assert "SMTP server unavailable" in failed_kwargs["error_message"]

    service.notification_service.mark_delivered.assert_called_once_with(
        notification_id=2,
        user_id=42,
    )

    assert result == {
        "processed": 2,
        "delivered": 1,
        "failed": 1,
        "skipped": 0,
    }


def test_delivery_skips_browser_push_notifications():
    email_notification = make_notification(1)
    push_notification = make_notification(
        2,
        channel="BROWSER_PUSH",
    )

    provider = Mock()
    service = make_service(
        [email_notification, push_notification],
        provider,
    )

    result = service.process_pending()

    provider.send.assert_called_once()
    service.notification_service.mark_delivered.assert_called_once_with(
        notification_id=1,
        user_id=41,
    )

    service.notification_service.mark_failed.assert_not_called()

    assert result == {
        "processed": 1,
        "delivered": 1,
        "failed": 0,
        "skipped": 1,
    }


def test_delivery_uses_pending_batch_limit():
    service = make_service([], Mock())

    result = service.process_pending(limit=25)

    service.repository.list_pending.assert_called_once_with(
        limit=25,
    )

    assert result == {
        "processed": 0,
        "delivered": 0,
        "failed": 0,
        "skipped": 0,
    }


def test_status_update_failure_does_not_stop_next_notification():
    first = make_notification(1)
    second = make_notification(2, user_id=42)

    provider = Mock()
    service = make_service(
        [first, second],
        provider,
    )

    service.notification_service.mark_delivered.side_effect = [
        RuntimeError("Database unavailable"),
        None,
    ]

    result = service.process_pending()

    assert provider.send.call_count == 2
    assert (
        service.notification_service.mark_delivered.call_count
        == 2
    )

    # A successful send with a failed status update is not counted
    # as a confirmed delivery by the worker.
    assert result == {
        "processed": 2,
        "delivered": 1,
        "failed": 0,
        "skipped": 0,
    }