
from app.models.history_event import HistoryEvent
from app.models.notification import Notification
from app.services.notification_preference_service import (
    NotificationPreferenceService,
)
from app.services.notification_service import NotificationService


class NotificationDecisionService:

    def __init__(self, db):
        self.preference_service = (
            NotificationPreferenceService(db)
        )
        self.notification_service = NotificationService(db)

    def create_notifications_for_event(
        self,
        event: HistoryEvent,
        user_id: int,
    ) -> list[Notification]:

        preference = (
            self.preference_service.get_preferences(
                user_id
            )
        )

        if not self._should_notify_for_event(
            event=event,
            preference=preference,
        ):
            return []

        channels = self._get_enabled_channels(
            preference
        )

        notifications = []

        for channel in channels:
            notification = (
                self.notification_service.create_notification(
                    history_event_id=event.id,
                    notification_channel=channel,
                )
            )

            notifications.append(notification)

        return notifications

    @staticmethod
    def _should_notify_for_event(
        event: HistoryEvent,
        preference,
    ) -> bool:

        event_type = event.event_type.upper()

        if event_type in {
            "PRICE_DROP",
            "PRICE_INCREASE",
            "PRICE_CHANGE",
        }:
            return preference.notify_on_price_change

        if event_type in {
            "STOCK_AVAILABLE",
            "STOCK_UNAVAILABLE",
            "AVAILABILITY_CHANGED",
        }:
            return preference.notify_on_stock_change

        return False

    @staticmethod
    def _get_enabled_channels(
        preference,
    ) -> list[str]:

        channels = []

        if preference.email_enabled:
            channels.append("EMAIL")

        if preference.browser_push_enabled:
            channels.append("BROWSER_PUSH")

        return channels
