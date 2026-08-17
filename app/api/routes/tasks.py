from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.task import CreateTaskRequest, TaskResponse,UpdateTaskRequest
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

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringTaskService(db)

    return service.get_task(
        task_id=task_id,
        user_id=current_user.id,
    )

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    request: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringTaskService(db)

    return service.update_task(
        task_id=task_id,
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        target_url=str(request.target_url),
        check_interval=request.check_interval,
    )

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringTaskService(db)

    service.delete_task(
        task_id=task_id,
        user_id=current_user.id,
    )

@router.post(
    "/{task_id}/pause",
)
def pause_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringTaskService(db)

    task = service.pause_task(
        task_id=task_id,
        user_id=current_user.id,
    )

    return {
        "message": "Monitoring task paused.",
        "is_active": task.is_active,
    }


@router.post(
    "/{task_id}/resume",
)
def resume_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringTaskService(db)

    task = service.resume_task(
        task_id=task_id,
        user_id=current_user.id,
    )

    return {
        "message": "Monitoring task resumed.",
        "is_active": task.is_active,
    }