
import pytest

from app.core.exceptions import ResourceNotFoundError
from app.database.session import SessionLocal
from app.models.user import User
from app.services.browser_push_subscription_service import (
    BrowserPushSubscriptionService,
)


def create_test_user(db, email: str, name: str) -> User:
    user = User(
        full_name=name,
        email=email,
        password_hash="test-password-hash",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_register_browser_push_subscription():
    db = SessionLocal()

    try:
        user = create_test_user(
            db,
            "browser-push-register@example.com",
            "Browser Push User",
        )
        service = BrowserPushSubscriptionService(db)

        subscription = service.register_subscription(
            user_id=user.id,
            endpoint="https://push.example.com/subscription/one",
            p256dh_key="test-p256dh-key",
            auth_key="test-auth-key",
        )

        assert subscription.id is not None
        assert subscription.user_id == user.id
        assert subscription.endpoint == (
            "https://push.example.com/subscription/one"
        )
        assert subscription.p256dh_key == "test-p256dh-key"
        assert subscription.auth_key == "test-auth-key"
        assert subscription.created_at is not None

    finally:
        db.query(User).filter(
            User.email == "browser-push-register@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_registering_same_endpoint_updates_existing_subscription():
    db = SessionLocal()

    try:
        user = create_test_user(
            db,
            "browser-push-update@example.com",
            "Browser Push User",
        )
        service = BrowserPushSubscriptionService(db)

        first = service.register_subscription(
            user_id=user.id,
            endpoint="https://push.example.com/subscription/update",
            p256dh_key="old-p256dh",
            auth_key="old-auth",
        )

        second = service.register_subscription(
            user_id=user.id,
            endpoint="https://push.example.com/subscription/update",
            p256dh_key="new-p256dh",
            auth_key="new-auth",
        )

        assert second.id == first.id
        assert second.p256dh_key == "new-p256dh"
        assert second.auth_key == "new-auth"

        subscriptions = service.list_subscriptions(user.id)
        assert len(subscriptions) == 1

    finally:
        db.query(User).filter(
            User.email == "browser-push-update@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_endpoint_cannot_be_registered_to_another_user():
    db = SessionLocal()

    try:
        first_user = create_test_user(
            db,
            "browser-push-owner@example.com",
            "First User",
        )
        second_user = create_test_user(
            db,
            "browser-push-other@example.com",
            "Second User",
        )

        service = BrowserPushSubscriptionService(db)

        original = service.register_subscription(
            user_id=first_user.id,
            endpoint="https://push.example.com/subscription/shared",
            p256dh_key="owner-p256dh",
            auth_key="owner-auth",
        )

        with pytest.raises(ValueError):
            service.register_subscription(
                user_id=second_user.id,
                endpoint="https://push.example.com/subscription/shared",
                p256dh_key="other-p256dh",
                auth_key="other-auth",
            )

        db.expire_all()

        subscriptions = service.list_subscriptions(first_user.id)
        assert len(subscriptions) == 1
        assert subscriptions[0].id == original.id
        assert subscriptions[0].p256dh_key == "owner-p256dh"
        assert service.list_subscriptions(second_user.id) == []

    finally:
        db.query(User).filter(
            User.email.in_([
                "browser-push-owner@example.com",
                "browser-push-other@example.com",
            ])
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_list_subscriptions_is_scoped_to_user():
    db = SessionLocal()

    try:
        first_user = create_test_user(
            db,
            "browser-push-list-first@example.com",
            "First User",
        )
        second_user = create_test_user(
            db,
            "browser-push-list-second@example.com",
            "Second User",
        )

        service = BrowserPushSubscriptionService(db)

        first_subscription = service.register_subscription(
            user_id=first_user.id,
            endpoint="https://push.example.com/subscription/first",
            p256dh_key="first-p256dh",
            auth_key="first-auth",
        )

        service.register_subscription(
            user_id=second_user.id,
            endpoint="https://push.example.com/subscription/second",
            p256dh_key="second-p256dh",
            auth_key="second-auth",
        )

        first_user_subscriptions = service.list_subscriptions(
            first_user.id
        )

        assert len(first_user_subscriptions) == 1
        assert first_user_subscriptions[0].id == first_subscription.id

    finally:
        db.query(User).filter(
            User.email.in_([
                "browser-push-list-first@example.com",
                "browser-push-list-second@example.com",
            ])
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_delete_subscription_requires_ownership():
    db = SessionLocal()

    try:
        user = create_test_user(
            db,
            "browser-push-delete@example.com",
            "Browser Push User",
        )
        service = BrowserPushSubscriptionService(db)

        subscription = service.register_subscription(
            user_id=user.id,
            endpoint="https://push.example.com/subscription/delete",
            p256dh_key="test-p256dh",
            auth_key="test-auth",
        )

        with pytest.raises(ResourceNotFoundError):
            service.delete_subscription(
                subscription_id=subscription.id,
                user_id=999999999,
            )

        service.delete_subscription(
            subscription_id=subscription.id,
            user_id=user.id,
        )

        assert service.list_subscriptions(user.id) == []

    finally:
        db.query(User).filter(
            User.email == "browser-push-delete@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()


def test_register_subscription_rejects_missing_keys():
    db = SessionLocal()

    try:
        user = create_test_user(
            db,
            "browser-push-invalid@example.com",
            "Browser Push User",
        )
        service = BrowserPushSubscriptionService(db)

        with pytest.raises(ValueError):
            service.register_subscription(
                user_id=user.id,
                endpoint="https://push.example.com/subscription/invalid",
                p256dh_key="",
                auth_key="test-auth",
            )

    finally:
        db.query(User).filter(
            User.email == "browser-push-invalid@example.com"
        ).delete(synchronize_session=False)
        db.commit()
        db.close()
