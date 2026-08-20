import bcrypt
import pytest
from sqlalchemy import delete

from app.database.session import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)


TEST_EMAILS = {
    "test@example.com",
    "duplicate@example.com",
    "login@example.com",
    "wrong-password@example.com",
    "short@example.com",
    "does-not-exist@example.com",
}


@pytest.fixture(autouse=True)
def clean_auth_test_users():
    db = SessionLocal()

    try:
        db.execute(
            delete(User).where(User.email.in_(TEST_EMAILS))
        )
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()

    try:
        db.execute(
            delete(User).where(User.email.in_(TEST_EMAILS))
        )
        db.commit()
    finally:
        db.close()


def test_register_user():
    db = SessionLocal()

    try:
        service = AuthService(db)

        user = service.register_user(
            full_name="Test User",
            email="  TEST@Example.COM  ",
            password="testpassword",
        )

        assert user.full_name == "Test User"
        assert user.email == "test@example.com"
        assert user.password_hash != "testpassword"

        assert bcrypt.checkpw(
            b"testpassword",
            user.password_hash.encode("utf-8"),
        )

    finally:
        db.close()


def test_register_user_rejects_short_password():
    db = SessionLocal()

    try:
        service = AuthService(db)

        with pytest.raises(ValueError, match="at least 8 characters"):
            service.register_user(
                full_name="Test User",
                email="short@example.com",
                password="abc123",
            )

    finally:
        db.close()


def test_register_user_rejects_duplicate_email():
    db = SessionLocal()

    try:
        service = AuthService(db)

        service.register_user(
            full_name="First User",
            email="duplicate@example.com",
            password="testpassword",
        )

        with pytest.raises(
            EmailAlreadyRegisteredError,
            match="Email already registered",
        ):
            service.register_user(
                full_name="Second User",
                email="DUPLICATE@example.com",
                password="anotherpassword",
            )

    finally:
        db.close()


def test_login_user_returns_access_token():
    db = SessionLocal()

    try:
        service = AuthService(db)

        service.register_user(
            full_name="Login Test",
            email="login@example.com",
            password="testpassword",
        )

        token = service.login_user(
            email="LOGIN@example.com",
            password="testpassword",
        )

        assert token

    finally:
        db.close()


def test_login_user_rejects_wrong_password():
    db = SessionLocal()

    try:
        service = AuthService(db)

        service.register_user(
            full_name="Login Test",
            email="wrong-password@example.com",
            password="testpassword",
        )

        with pytest.raises(
            InvalidCredentialsError,
            match="Invalid credentials",
        ):
            service.login_user(
                email="wrong-password@example.com",
                password="wrongpassword",
            )

    finally:
        db.close()


def test_login_user_rejects_unknown_email():
    db = SessionLocal()

    try:
        service = AuthService(db)

        with pytest.raises(
            InvalidCredentialsError,
            match="Invalid credentials",
        ):
            service.login_user(
                email="does-not-exist@example.com",
                password="testpassword",
            )

    finally:
        db.close()