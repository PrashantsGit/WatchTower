from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.notification_preference import NotificationPreference
from app.repositories.notification_preference_repository import (
    NotificationPreferenceRepository,
)


class NotificationPreferenceService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationPreferenceRepository(db)

    def create_default_preferences(
        self,
        user_id: int,
    ) -> NotificationPreference:

        preference = NotificationPreference(
            user_id=user_id,
        )

        try:
            preference = self.repository.create(
                preference
            )

            self.db.commit()
            self.db.refresh(preference)

            return preference

        except Exception:
            self.db.rollback()
            raise

    def get_preferences(
        self,
        user_id: int,
    ) -> NotificationPreference:

        preference = self.repository.find_by_user_id(
            user_id
        )

        if preference is None:
            raise ResourceNotFoundError(
                "Notification preferences not found."
            )

        return preference

    def update_preferences(
        self,
        user_id: int,
        email_enabled: bool | None = None,
        browser_push_enabled: bool | None = None,
        notify_on_price_change: bool | None = None,
        notify_on_stock_change: bool | None = None,
    ) -> NotificationPreference:

        preference = self.get_preferences(
            user_id
        )

        if email_enabled is not None:
            preference.email_enabled = email_enabled

        if browser_push_enabled is not None:
            preference.browser_push_enabled = (
                browser_push_enabled
            )

        if notify_on_price_change is not None:
            preference.notify_on_price_change = (
                notify_on_price_change
            )

        if notify_on_stock_change is not None:
            preference.notify_on_stock_change = (
                notify_on_stock_change
            )

        try:
            preference = self.repository.update(
                preference
            )

            self.db.commit()
            self.db.refresh(preference)

            return preference

        except Exception:
            self.db.rollback()
            raise