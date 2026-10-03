import logging

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.notifications.providers import (
    NotificationProvider,
    SMTPEmailProvider,
)
from app.repositories.notification_repository import (
    NotificationRepository,
)
from app.services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    """Deliver persisted notifications independently of monitoring."""

    def __init__(
        self,
        db: Session,
        email_provider: NotificationProvider | None = None,
    ):
        self.db = db
        self.repository = NotificationRepository(db)
        self.notification_service = NotificationService(db)
        self.email_provider = (
            email_provider or SMTPEmailProvider()
        )

    def process_pending(
        self,
        limit: int = 100,
    ) -> dict[str, int]:
        notifications = self.repository.list_pending(
            limit=limit,
        )

        result = {
            "processed": 0,
            "delivered": 0,
            "failed": 0,
            "skipped": 0,
        }

        for notification in notifications:
            if notification.notification_channel.upper() != "EMAIL":
                # Other providers will be registered in later stages.
                result["skipped"] += 1
                continue

            result["processed"] += 1
            self._deliver_email(
                notification=notification,
                result=result,
            )

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

            try:
                self.notification_service.mark_failed(
                    notification_id=notification.id,
                    user_id=task.user_id,
                    error_message=self._safe_error_message(exc),
                )
                result["failed"] += 1
            except Exception:
                # A status update failure must not stop other notifications.
                logger.exception(
                    "Could not mark notification %s as failed",
                    notification.id,
                )
            return

        try:
            self.notification_service.mark_delivered(
                notification_id=notification.id,
                user_id=task.user_id,
            )
            result["delivered"] += 1
        except Exception:
            # Sending may have succeeded even if status persistence failed.
            # Log this separately because the delivery outcome is uncertain.
            logger.exception(
                "Email was sent, but delivery status could not be "
                "updated for notification %s",
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
            lines.extend(
                [
                    "",
                    f"Details: {event.event_message}",
                ]
            )

        if event.previous_value is not None:
            lines.append(
                f"Previous value: {event.previous_value}"
            )

        if event.current_value is not None:
            lines.append(
                f"Current value: {event.current_value}"
            )

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
        # Keep stored errors bounded; avoid logging SMTP credentials.
        message = f"{type(error).__name__}: {error}"
        return message[:max_length]