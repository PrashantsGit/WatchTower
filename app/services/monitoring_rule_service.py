from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_task import MonitoringTask
from app.repositories.monitoring_rule_repository import MonitoringRuleRepository


class MonitoringRuleService:

    PRICE_OPERATORS = {
        "<",
        "<=",
        "==",
        ">=",
        ">",
    }

    AVAILABILITY_OPERATORS = {
        "==",
        "!=",
    }

    KEYWORD_OPERATORS = {
        "CONTAINS",
        "NOT_CONTAINS",
    }

    AVAILABILITY_TARGETS = {
        "IN_STOCK",
        "OUT_OF_STOCK",
    }

    def __init__(self, db: Session):
        self.db = db
        self.rule_repository = MonitoringRuleRepository(db)

    def _get_owned_task(
        self,
        task_id: int,
        user_id: int,
    ) -> MonitoringTask:
        task = self.db.get(MonitoringTask, task_id)

        if task is None or task.user_id != user_id:
            raise ResourceNotFoundError("Monitoring task not found.")

        return task

    def _validate_rule(
        self,
        rule_type: str,
        operator: str,
        target_value: str,
    ) -> str:
        rule_type = rule_type.strip().upper()
        operator = operator.strip().upper()
        target_value = target_value.strip()

        if rule_type == "PRICE":
            if operator not in self.PRICE_OPERATORS:
                raise ValueError(
                    "Invalid operator for PRICE rule."
                )

            if not target_value.isdigit() or int(target_value) <= 0:
                raise ValueError(
                    "Price target must be a positive integer."
                )

        elif rule_type == "AVAILABILITY":
            if operator not in self.AVAILABILITY_OPERATORS:
                raise ValueError(
                    "Invalid operator for AVAILABILITY rule."
                )

            if target_value not in self.AVAILABILITY_TARGETS:
                raise ValueError(
                    "Invalid availability target."
                )

        elif rule_type == "KEYWORD":
            if operator not in self.KEYWORD_OPERATORS:
                raise ValueError(
                    "Invalid operator for KEYWORD rule."
                )

            if not target_value:
                raise ValueError(
                    "Keyword target cannot be empty."
                )

        else:
            raise ValueError(
                "Invalid rule type."
            )

        return rule_type

    def create_rule(
        self,
        task_id: int,
        user_id: int,
        rule_type: str,
        operator: str,
        target_value: str,
    ) -> MonitoringRule:
        self._get_owned_task(
            task_id=task_id,
            user_id=user_id,
        )

        rule_type = self._validate_rule(
            rule_type=rule_type,
            operator=operator,
            target_value=target_value,
        )

        rule = MonitoringRule(
            task_id=task_id,
            rule_type=rule_type,
            operator=operator.strip().upper(),
            target_value=target_value.strip(),
            is_enabled=True,
        )

        try:
            rule = self.rule_repository.create(rule)
            self.db.commit()
            self.db.refresh(rule)
            return rule

        except Exception:
            self.db.rollback()
            raise

    def list_rules(
        self,
        task_id: int,
        user_id: int,
    ) -> list[MonitoringRule]:
        self._get_owned_task(
            task_id=task_id,
            user_id=user_id,
        )

        return self.rule_repository.list_by_task(task_id)

    def get_rule(
        self,
        rule_id: int,
        task_id: int,
        user_id: int,
    ) -> MonitoringRule:
        self._get_owned_task(
            task_id=task_id,
            user_id=user_id,
        )

        rule = self.rule_repository.find_by_id(rule_id)

        if rule is None or rule.task_id != task_id:
            raise ResourceNotFoundError("Monitoring rule not found.")

        return rule

    def update_rule(
        self,
        rule_id: int,
        task_id: int,
        user_id: int,
        rule_type: str,
        operator: str,
        target_value: str,
        is_enabled: bool,
    ) -> MonitoringRule:
        self._get_owned_task(
            task_id=task_id,
            user_id=user_id,
        )

        rule = self.rule_repository.find_by_id(rule_id)

        if rule is None or rule.task_id != task_id:
            raise ResourceNotFoundError("Monitoring rule not found.")

        rule_type = self._validate_rule(
            rule_type=rule_type,
            operator=operator,
            target_value=target_value,
        )

        rule.rule_type = rule_type
        rule.operator = operator.strip().upper()
        rule.target_value = target_value.strip()
        rule.is_enabled = is_enabled

        try:
            rule = self.rule_repository.update(rule)
            self.db.commit()
            self.db.refresh(rule)
            return rule

        except Exception:
            self.db.rollback()
            raise

    def delete_rule(
        self,
        rule_id: int,
        task_id: int,
        user_id: int,
    ) -> None:
        self._get_owned_task(
            task_id=task_id,
            user_id=user_id,
        )

        rule = self.rule_repository.find_by_id(rule_id)

        if rule is None or rule.task_id != task_id:
            raise ResourceNotFoundError("Monitoring rule not found.")

        try:
            self.rule_repository.delete(rule)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise