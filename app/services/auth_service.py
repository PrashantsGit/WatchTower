from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
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
            raise ValueError("Password must be at least 8 characters long.")

        existing_user = self.user_repository.find_by_email(email)

        if existing_user:
            raise ValueError("Email already registered.")

        password_hash = hash_password(password)

        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
        )

        return self.user_repository.create(user)

    def login_user(
        self,
        email: str,
        password: str,
    ) -> str:
        email = email.strip().lower()

        user = self.user_repository.find_by_email(email)

        if not user:
            raise ValueError("Invalid credentials.")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials.")

        if not user.is_active:
            raise ValueError("Invalid credentials.")

        return create_access_token(user.id)