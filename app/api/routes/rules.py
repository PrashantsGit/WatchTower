from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.rule import (
    CreateRuleRequest,
    RuleResponse,
    UpdateRuleRequest,
)
from app.services.monitoring_rule_service import MonitoringRuleService


router = APIRouter(
    prefix="/tasks/{task_id}/rules",
    tags=["Monitoring Rules"],
)


@router.post(
    "",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rule(
    task_id: int,
    request: CreateRuleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringRuleService(db)

    return service.create_rule(
        task_id=task_id,
        user_id=current_user.id,
        rule_type=request.rule_type,
        operator=request.operator,
        target_value=request.target_value,
    )


@router.get(
    "",
    response_model=list[RuleResponse],
)
def list_rules(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringRuleService(db)

    return service.list_rules(
        task_id=task_id,
        user_id=current_user.id,
    )


@router.get(
    "/{rule_id}",
    response_model=RuleResponse,
)
def get_rule(
    task_id: int,
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringRuleService(db)

    return service.get_rule(
        rule_id=rule_id,
        task_id=task_id,
        user_id=current_user.id,
    )


@router.put(
    "/{rule_id}",
    response_model=RuleResponse,
)
def update_rule(
    task_id: int,
    rule_id: int,
    request: UpdateRuleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringRuleService(db)

    return service.update_rule(
        rule_id=rule_id,
        task_id=task_id,
        user_id=current_user.id,
        rule_type=request.rule_type,
        operator=request.operator,
        target_value=request.target_value,
        is_enabled=request.is_enabled,
    )


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rule(
    task_id: int,
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MonitoringRuleService(db)

    service.delete_rule(
        rule_id=rule_id,
        task_id=task_id,
        user_id=current_user.id,
    )