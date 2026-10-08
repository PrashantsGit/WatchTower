from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.history import HistoryEventResponse
from app.services.history_event_service import HistoryEventService


router = APIRouter(
    tags=["History"],
)


@router.get(
    "/history",
    response_model=list[HistoryEventResponse],
)
def list_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = HistoryEventService(db)

    return service.list_events_for_user(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/tasks/{task_id}/history",
    response_model=list[HistoryEventResponse],
)
def list_task_history(
    task_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = HistoryEventService(db)

    return service.list_events_for_task(
        task_id=task_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )