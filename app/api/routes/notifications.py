from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.notification_preference import (
    NotificationPreferenceResponse,
    UpdateNotificationPreferenceRequest,
)
from app.services.notification_preference_service import (
    NotificationPreferenceService,
)
from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def list_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    return service.list_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/preferences",
    response_model=NotificationPreferenceResponse,
)
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationPreferenceService(db)

    return service.get_preferences(
        user_id=current_user.id,
    )


@router.put(
    "/preferences",
    response_model=NotificationPreferenceResponse,
)
def update_notification_preferences(
    request: UpdateNotificationPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationPreferenceService(db)

    return service.update_preferences(
        user_id=current_user.id,
        **request.model_dump(exclude_unset=True),
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    return service.get_notification(
        notification_id=notification_id,
        user_id=current_user.id,
    )