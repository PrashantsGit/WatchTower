
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    __table_args__ = (
        UniqueConstraint(
            "jti",
            name="uq_revoked_tokens_jti",
        ),
        Index(
            "idx_revoked_tokens_expires_at",
            "expires_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        name="id",
    )

    jti: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
