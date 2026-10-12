
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


class RevokedTokenRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_jti(self, jti: str) -> RevokedToken | None:
        statement = select(RevokedToken).where(
            RevokedToken.jti == jti,
        )
        return self.db.scalar(statement)

    def create(self, revoked_token: RevokedToken) -> RevokedToken:
        self.db.add(revoked_token)
        self.db.flush()
        self.db.refresh(revoked_token)
        return revoked_token
