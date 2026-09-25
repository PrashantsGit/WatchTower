import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ResourceNotFoundError
from app.models.user import User
from app.services.notification_preference_service import (
    NotificationPreferenceService,
)
from app.database.session import SessionLocal


def create_test_user(db):
    user = User(
        full_name="Notification Test User",
        email="notification-test@example.com",
        password_hash="test-password-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def test_create_default_preferences():
    db = SessionLocal()

    try:
        user = create_test_user(db)

        service = NotificationPreferenceService(db)

        preference = service.create_default_preferences(
            user_id=user.id
        )

        assert preference.id is not None
        assert preference.user_id == user.id
        assert preference.email_enabled is True
        assert preference.browser_push_enabled is True
        assert preference.notify_on_price_change is True
        assert preference.notify_on_stock_change is True

    finally:
        db.query(User).filter(
            User.email == "notification-test@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_get_preferences():
    db = SessionLocal()

    try:
        user = create_test_user(db)

        service = NotificationPreferenceService(db)

        created = service.create_default_preferences(
            user_id=user.id
        )

        preference = service.get_preferences(
            user_id=user.id
        )

        assert preference.id == created.id
        assert preference.user_id == user.id

    finally:
        db.query(User).filter(
            User.email == "notification-test@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_get_preferences_raises_when_missing():
    db = SessionLocal()

    try:
        service = NotificationPreferenceService(db)

        with pytest.raises(ResourceNotFoundError):
            service.get_preferences(
                user_id=999999999
            )

    finally:
        db.close()


def test_update_preferences():
    db = SessionLocal()

    try:
        user = create_test_user(db)

        service = NotificationPreferenceService(db)

        service.create_default_preferences(
            user_id=user.id
        )

        updated = service.update_preferences(
            user_id=user.id,
            email_enabled=False,
            browser_push_enabled=False,
            notify_on_price_change=False,
            notify_on_stock_change=True,
        )

        assert updated.email_enabled is False
        assert updated.browser_push_enabled is False
        assert updated.notify_on_price_change is False
        assert updated.notify_on_stock_change is True

    finally:
        db.query(User).filter(
            User.email == "notification-test@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()


def test_duplicate_preferences_are_rejected():
    db = SessionLocal()

    try:
        user = create_test_user(db)

        service = NotificationPreferenceService(db)

        service.create_default_preferences(
            user_id=user.id
        )

        with pytest.raises(IntegrityError):
            service.create_default_preferences(
                user_id=user.id
            )

        db.rollback()

    finally:
        db.query(User).filter(
            User.email == "notification-test@example.com"
        ).delete(
            synchronize_session=False
        )
        db.commit()
        db.close()