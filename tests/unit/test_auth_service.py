import bcrypt
import pytest

from app.database.session import SessionLocal
from app.services.auth_service import AuthService


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
        db.rollback()
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
        db.rollback()
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

        with pytest.raises(ValueError, match="Email already registered"):
            service.register_user(
                full_name="Second User",
                email="DUPLICATE@example.com",
                password="anotherpassword",
            )

    finally:
        db.rollback()
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
        db.rollback()
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

        with pytest.raises(ValueError, match="Invalid credentials"):
            service.login_user(
                email="wrong-password@example.com",
                password="wrongpassword",
            )

    finally:
        db.rollback()
        db.close()


def test_login_user_rejects_unknown_email():
    db = SessionLocal()

    try:
        service = AuthService(db)

        with pytest.raises(ValueError, match="Invalid credentials"):
            service.login_user(
                email="does-not-exist@example.com",
                password="testpassword",
            )

    finally:
        db.rollback()
        db.close()