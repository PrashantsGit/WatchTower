from dataclasses import dataclass

from app.models.monitoring_rule import MonitoringRule
from app.monitoring.evaluator import RuleEvaluationResult


@dataclass
class MonitoringTrigger:
    rule: MonitoringRule


class MonitoringTriggerService:

    def get_triggered_rules(
        self,
        evaluations: list[RuleEvaluationResult],
    ) -> list[RuleEvaluationResult]:

        return [
            evaluation
            for evaluation in evaluations
            if evaluation.matched
        ]

    def should_trigger(
        self,
        evaluations: list[RuleEvaluationResult],
    ) -> bool:

        return any(
            evaluation.matched
            for evaluation in evaluations
        )