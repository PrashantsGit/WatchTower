
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.browser_push_subscription import BrowserPushSubscription
from app.repositories.browser_push_subscription_repository import (
    BrowserPushSubscriptionRepository,
)


class BrowserPushSubscriptionService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = BrowserPushSubscriptionRepository(db)

    def register_subscription(
        self,
        user_id: int,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        expiration_time: datetime | None = None,
    ) -> BrowserPushSubscription:
        endpoint = endpoint.strip()
        p256dh_key = p256dh_key.strip()
        auth_key = auth_key.strip()

        if not endpoint or not p256dh_key or not auth_key:
            raise ValueError(
                "Endpoint and subscription keys are required."
            )

        existing = self.repository.find_by_endpoint(endpoint)

        try:
            if existing is not None:
                if existing.user_id != user_id:
                    raise ValueError(
                        "This browser subscription is already registered "
                        "to another user."
                    )

                existing.p256dh_key = p256dh_key
                existing.auth_key = auth_key
                existing.expiration_time = expiration_time

                subscription = self.repository.update(existing)
            else:
                subscription = self.repository.create(
                    BrowserPushSubscription(
                        user_id=user_id,
                        endpoint=endpoint,
                        p256dh_key=p256dh_key,
                        auth_key=auth_key,
                        expiration_time=expiration_time,
                    )
                )

            self.db.commit()
            self.db.refresh(subscription)
            return subscription

        except Exception:
            self.db.rollback()
            raise

    def list_subscriptions(
        self,
        user_id: int,
    ) -> list[BrowserPushSubscription]:
        return self.repository.list_for_user(user_id)

    def delete_subscription(
        self,
        subscription_id: int,
        user_id: int,
    ) -> None:
        subscription = self.repository.find_by_id_for_user(
            subscription_id=subscription_id,
            user_id=user_id,
        )

        if subscription is None:
            raise ResourceNotFoundError(
                "Browser push subscription not found."
            )

        try:
            self.repository.delete(subscription)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
