from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.notification_preference import (
    NotificationPreference,
)
from app.models.user import User
from app.repositories.notification_preference_repository import (
    NotificationPreferenceRepository,
)
from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)


class AuthService:

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.notification_preference_repository = (
            NotificationPreferenceRepository(db)
        )
        self.db = db

    def register_user(
        self,
        full_name: str,
        email: str,
        password: str,
    ) -> User:

        email = email.strip().lower()
        full_name = full_name.strip()

        if len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters long."
            )

        existing_user = self.user_repository.find_by_email(
            email
        )

        if existing_user:
            raise EmailAlreadyRegisteredError(
                "Email already registered."
            )

        password_hash = hash_password(password)

        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
        )

        try:
            user = self.user_repository.create(user)

            preference = NotificationPreference(
                user_id=user.id,
            )

            self.notification_preference_repository.create(
                preference
            )

            self.db.commit()
            self.db.refresh(user)

            return user

        except Exception:
            self.db.rollback()
            raise

    def login_user(
        self,
        email: str,
        password: str,
    ) -> str:

        email = email.strip().lower()

        user = self.user_repository.find_by_email(
            email
        )

        if not user:
            raise InvalidCredentialsError(
                "Invalid credentials."
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsError(
                "Invalid credentials."
            )

        if not user.is_active:
            raise InvalidCredentialsError(
                "Invalid credentials."
            )

        return create_access_token(user.id)