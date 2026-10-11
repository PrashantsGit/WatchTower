
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def get_profile(self, user_id: int) -> User | None:
        """Return a user's profile record."""
        return self.user_repository.find_by_id(user_id)

    def update_profile(self, user_id: int, full_name: str) -> User | None:
        """Update a user's display name."""
        user = self.user_repository.find_by_id(user_id)

        if user is None:
            return None

        normalized_name = full_name.strip()
        if not normalized_name:
            raise ValueError("Full name cannot be blank.")

        user.full_name = normalized_name

        try:
            updated_user = self.user_repository.update(user)
            self.db.commit()
            self.db.refresh(updated_user)
            return updated_user
        except Exception:
            self.db.rollback()
            raise
