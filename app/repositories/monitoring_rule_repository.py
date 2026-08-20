from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monitoring_rule import MonitoringRule


class MonitoringRuleRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, rule: MonitoringRule) -> MonitoringRule:
        self.db.add(rule)
        self.db.flush()
        self.db.refresh(rule)
        return rule

    def find_by_id(
        self,
        rule_id: int,
    ) -> MonitoringRule | None:
        statement = select(MonitoringRule).where(
            MonitoringRule.id == rule_id,
        )

        return self.db.scalar(statement)

    def list_by_task(
        self,
        task_id: int,
    ) -> list[MonitoringRule]:
        statement = (
            select(MonitoringRule)
            .where(MonitoringRule.task_id == task_id)
            .order_by(MonitoringRule.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update(self, rule: MonitoringRule) -> MonitoringRule:
        self.db.flush()
        self.db.refresh(rule)
        return rule

    def delete(self, rule: MonitoringRule) -> None:
        self.db.delete(rule)
        self.db.flush()