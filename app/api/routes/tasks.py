from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.task import CreateTaskRequest, TaskResponse
from app.services.monitoring_task_service import MonitoringTaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Monitoring Tasks"],
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringTaskService(db)

    return service.create_task(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        target_url=str(request.target_url),
        check_interval=request.check_interval,
    )


@router.get(
    "",
    response_model=list[TaskResponse],
)
def list_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringTaskService(db)

    return service.list_tasks(
        user_id=current_user.id,
    )