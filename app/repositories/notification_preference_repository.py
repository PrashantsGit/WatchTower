from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification_preference import NotificationPreference


class NotificationPreferenceRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        preference: NotificationPreference,
    ) -> NotificationPreference:

        self.db.add(preference)
        self.db.flush()
        self.db.refresh(preference)

        return preference

    def find_by_user_id(
        self,
        user_id: int,
    ) -> NotificationPreference | None:

        statement = select(
            NotificationPreference
        ).where(
            NotificationPreference.user_id == user_id,
        )

        return self.db.scalar(statement)

    def update(
        self,
        preference: NotificationPreference,
    ) -> NotificationPreference:

        self.db.flush()
        self.db.refresh(preference)

        return preference