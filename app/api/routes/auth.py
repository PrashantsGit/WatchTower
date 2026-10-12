from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.user import UserResponse

from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.revoked_token import RevokedToken
from app.core.security import decode_access_token
from app.repositories.revoked_token_repository import (
    RevokedTokenRepository,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    user = service.register_user(
        full_name=request.full_name,
        email=str(request.email),
        password=request.password,
    )

    return {
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
        },
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    access_token = service.login_user(
        email=str(request.email),
        password=request.password,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/logout")
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    jti = payload.get("jti")
    expires_at = payload.get("exp")

    if not isinstance(jti, str) or not jti or expires_at is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    repository = RevokedTokenRepository(db)

    if repository.find_by_jti(jti) is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    revoked_token = RevokedToken(
        jti=jti,
        expires_at=datetime.fromtimestamp(
            expires_at,
            tz=timezone.utc,
        ),
    )

    db.add(revoked_token)
    db.commit()

    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user