
import logging

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.notifications.providers import (
    ExpiredPushSubscriptionError,
    NotificationProvider,
    SMTPEmailProvider,
    WebPushProvider,
)
from app.repositories.browser_push_subscription_repository import (
    BrowserPushSubscriptionRepository,
)
from app.repositories.notification_repository import (
    NotificationRepository,
)
from app.services.browser_push_subscription_service import (
    BrowserPushSubscriptionService,
)
from app.services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    """Deliver persisted notifications independently of monitoring."""

    def __init__(
        self,
        db: Session,
        email_provider: NotificationProvider | None = None,
        push_provider: WebPushProvider | None = None,
    ):
        self.db = db
        self.repository = NotificationRepository(db)
        self.notification_service = NotificationService(db)
        self.browser_subscription_repository = (
            BrowserPushSubscriptionRepository(db)
        )
        self.browser_subscription_service = (
            BrowserPushSubscriptionService(db)
        )
        self.email_provider = email_provider or SMTPEmailProvider()
        self.push_provider = push_provider or WebPushProvider()

    def process_pending(
        self,
        limit: int = 100,
    ) -> dict[str, int]:
        notifications = self.repository.list_pending(limit=limit)

        result = {
            "processed": 0,
            "delivered": 0,
            "failed": 0,
            "skipped": 0,
        }

        for notification in notifications:
            channel = notification.notification_channel.upper()

            if channel not in {"EMAIL", "BROWSER_PUSH"}:
                result["skipped"] += 1
                continue

            result["processed"] += 1

            if channel == "EMAIL":
                self._deliver_email(notification, result)
            else:
                self._deliver_browser_push(notification, result)

        logger.info(
            "Notification delivery batch completed: %s",
            result,
        )
        return result

    def _deliver_email(
        self,
        notification: Notification,
        result: dict[str, int],
    ) -> None:
        event = notification.history_event
        task = event.task
        user = task.user

        subject = (
            f"WatchTower alert: {event.event_type.replace('_', ' ').title()}"
        )
        body = self._build_email_body(
            event=event,
            task_name=task.name,
            target_url=task.target_url,
        )

        try:
            self.email_provider.send(
                recipient_email=user.email,
                subject=subject,
                body=body,
            )
        except Exception as exc:
            logger.exception(
                "Email delivery failed for notification %s",
                notification.id,
            )
            self._mark_failed(
                notification=notification,
                error=exc,
                result=result,
            )
            return

        self._mark_delivered(
            notification=notification,
            result=result,
            channel_name="Email",
        )

    def _deliver_browser_push(
        self,
        notification: Notification,
        result: dict[str, int],
    ) -> None:
        event = notification.history_event
        task = event.task
        user_id = task.user_id

        subscriptions = (
            self.browser_subscription_repository.list_for_user(user_id)
        )

        if not subscriptions:
            self._mark_failed(
                notification=notification,
                error=RuntimeError(
                    "No browser push subscriptions are registered."
                ),
                result=result,
            )
            return

        title = (
            f"WatchTower alert: {event.event_type.replace('_', ' ').title()}"
        )
        body = self._build_email_body(
            event=event,
            task_name=task.name,
            target_url=task.target_url,
        )

        successful_deliveries = 0
        failures: list[str] = []

        for subscription in subscriptions:
            try:
                self.push_provider.send(
                    endpoint=subscription.endpoint,
                    p256dh_key=subscription.p256dh_key,
                    auth_key=subscription.auth_key,
                    title=title,
                    body=body,
                    target_url=task.target_url,
                )
                successful_deliveries += 1

            except ExpiredPushSubscriptionError as exc:
                logger.info(
                    "Removing expired browser subscription %s",
                    subscription.id,
                )
                try:
                    self.browser_subscription_service.delete_subscription(
                        subscription_id=subscription.id,
                        user_id=user_id,
                    )
                except Exception as delete_exc:
                    logger.exception(
                        "Could not remove expired browser subscription %s",
                        subscription.id,
                    )
                    failures.append(
                        self._safe_error_message(delete_exc)
                    )
                else:
                    failures.append(self._safe_error_message(exc))

            except Exception as exc:
                logger.exception(
                    "Browser push delivery failed for notification %s "
                    "and subscription %s",
                    notification.id,
                    subscription.id,
                )
                failures.append(self._safe_error_message(exc))

        if successful_deliveries:
            self._mark_delivered(
                notification=notification,
                result=result,
                channel_name="Browser push",
            )
            return

        error_message = "; ".join(failures) or (
            "Browser push delivery failed for all subscriptions."
        )
        self._mark_failed(
            notification=notification,
            error=RuntimeError(error_message),
            result=result,
        )

    def _mark_delivered(
        self,
        notification: Notification,
        result: dict[str, int],
        channel_name: str,
    ) -> None:
        try:
            self.notification_service.mark_delivered(
                notification_id=notification.id,
                user_id=notification.history_event.task.user_id,
            )
            result["delivered"] += 1
        except Exception:
            logger.exception(
                "%s was sent, but delivery status could not be updated "
                "for notification %s",
                channel_name,
                notification.id,
            )

    def _mark_failed(
        self,
        notification: Notification,
        error: Exception,
        result: dict[str, int],
    ) -> None:
        try:
            self.notification_service.mark_failed(
                notification_id=notification.id,
                user_id=notification.history_event.task.user_id,
                error_message=self._safe_error_message(error),
            )
            result["failed"] += 1
        except Exception:
            logger.exception(
                "Could not mark notification %s as failed",
                notification.id,
            )

    @staticmethod
    def _build_email_body(
        event,
        task_name: str,
        target_url: str,
    ) -> str:
        lines = [
            "A monitored condition has changed.",
            "",
            f"Task: {task_name}",
            f"Event: {event.event_type.replace('_', ' ').title()}",
        ]

        if event.event_message:
            lines.extend(["", f"Details: {event.event_message}"])

        if event.previous_value is not None:
            lines.append(f"Previous value: {event.previous_value}")

        if event.current_value is not None:
            lines.append(f"Current value: {event.current_value}")

        lines.extend(
            [
                "",
                f"Monitored URL: {target_url}",
                "",
                "You received this message because a WatchTower "
                "monitoring event matched your notification preferences.",
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def _safe_error_message(
        error: Exception,
        max_length: int = 1000,
    ) -> str:
        message = f"{type(error).__name__}: {error}"
        return message[:max_length]
