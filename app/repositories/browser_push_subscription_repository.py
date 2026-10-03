
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.browser_push_subscription import BrowserPushSubscription


class BrowserPushSubscriptionRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        subscription: BrowserPushSubscription,
    ) -> BrowserPushSubscription:
        self.db.add(subscription)
        self.db.flush()
        self.db.refresh(subscription)
        return subscription

    def find_by_endpoint(
        self,
        endpoint: str,
    ) -> BrowserPushSubscription | None:
        statement = select(BrowserPushSubscription).where(
            BrowserPushSubscription.endpoint == endpoint,
        )
        return self.db.scalar(statement)

    def find_by_id_for_user(
        self,
        subscription_id: int,
        user_id: int,
    ) -> BrowserPushSubscription | None:
        statement = select(BrowserPushSubscription).where(
            BrowserPushSubscription.id == subscription_id,
            BrowserPushSubscription.user_id == user_id,
        )
        return self.db.scalar(statement)

    def list_for_user(
        self,
        user_id: int,
    ) -> list[BrowserPushSubscription]:
        statement = (
            select(BrowserPushSubscription)
            .where(BrowserPushSubscription.user_id == user_id)
            .order_by(
                BrowserPushSubscription.created_at.desc(),
                BrowserPushSubscription.id.desc(),
            )
        )
        return list(self.db.scalars(statement).all())

    def delete(
        self,
        subscription: BrowserPushSubscription,
    ) -> None:
        self.db.delete(subscription)
        self.db.flush()

    def update(
        self,
        subscription: BrowserPushSubscription,
    ) -> BrowserPushSubscription:
        self.db.flush()
        self.db.refresh(subscription)
        return subscription
