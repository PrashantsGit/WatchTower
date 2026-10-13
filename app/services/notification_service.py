from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.notification import Notification
from app.repositories.notification_repository import (
    NotificationRepository,
)


class NotificationService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)

    def create_notification(
        self,
        history_event_id: int,
        notification_channel: str,
    ) -> Notification:
        notification = Notification(
            history_event_id=history_event_id,
            notification_channel=notification_channel.strip(),
            notification_status="PENDING",
        )

        try:
            notification = self.repository.create(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except Exception:
            self.db.rollback()
            raise

    def list_notifications(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Notification]:
        return self.repository.list_for_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    def get_notification(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification:
        notification = self.repository.find_by_id_for_user(
            notification_id=notification_id,
            user_id=user_id,
        )

        if notification is None:
            raise ResourceNotFoundError("Notification not found.")

        return notification

    def list_by_history_event(
        self,
        history_event_id: int,
        user_id: int,
    ) -> list[Notification]:
        return self.repository.list_by_history_event_for_user(
            history_event_id=history_event_id,
            user_id=user_id,
        )

    def mark_delivered(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification:
        notification = self.get_notification(
            notification_id=notification_id,
            user_id=user_id,
        )

        notification.notification_status = "DELIVERED"
        notification.delivered_at = datetime.now(timezone.utc)
        notification.error_message = None

        try:
            notification = self.repository.update(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except Exception:
            self.db.rollback()
            raise

    def mark_failed(
        self,
        notification_id: int,
        user_id: int,
        error_message: str,
    ) -> Notification:
        notification = self.get_notification(
            notification_id=notification_id,
            user_id=user_id,
        )

        notification.notification_status = "FAILED"
        notification.delivered_at = None
        notification.error_message = error_message

        try:
            notification = self.repository.update(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except Exception:
            self.db.rollback()
            raise
    
    def mark_as_read(
        self,
        notification_id: int,
        user_id: int,
    ) -> Notification:
        notification = self.get_notification(
            notification_id=notification_id,
            user_id=user_id,
        )

        try:
            if notification.read_at is None:
                notification.read_at = datetime.now(timezone.utc)

            notification = self.repository.update(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except Exception:
            self.db.rollback()
            raise

    def delete_notification(
        self,
        notification_id: int,
        user_id: int,
    ) -> None:
        notification = self.get_notification(
            notification_id=notification_id,
            user_id=user_id,
        )

        try:
            self.repository.delete(notification)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
