
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.browser_push_subscription import (
    BrowserPushSubscriptionResponse,
    RegisterBrowserPushSubscriptionRequest,
)
from app.schemas.notification import NotificationResponse
from app.schemas.notification_preference import (
    NotificationPreferenceResponse,
    UpdateNotificationPreferenceRequest,
)
from app.services.browser_push_subscription_service import (
    BrowserPushSubscriptionService,
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


@router.post(
    "/push-subscriptions",
    response_model=BrowserPushSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_browser_push_subscription(
    request: RegisterBrowserPushSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BrowserPushSubscriptionService(db)

    try:
        return service.register_subscription(
            user_id=current_user.id,
            endpoint=request.endpoint,
            p256dh_key=request.keys.p256dh,
            auth_key=request.keys.auth,
            expiration_time=request.expiration_time,
        )
    except ValueError as exc:
        message = str(exc)

        if "already registered to another user" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
        ) from exc


@router.get(
    "/push-subscriptions",
    response_model=list[BrowserPushSubscriptionResponse],
)
def list_browser_push_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BrowserPushSubscriptionService(db)

    return service.list_subscriptions(
        user_id=current_user.id,
    )


@router.delete(
    "/push-subscriptions/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_browser_push_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BrowserPushSubscriptionService(db)

    service.delete_subscription(
        subscription_id=subscription_id,
        user_id=current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    return service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    service.delete_notification(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
