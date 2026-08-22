from dataclasses import dataclass

from app.models.monitoring_rule import MonitoringRule
from app.monitoring.extractor import ExtractedData


@dataclass
class RuleEvaluationResult:
    rule: MonitoringRule
    matched: bool


class MonitoringRuleEvaluator:

    def evaluate(
        self,
        rule: MonitoringRule,
        data: ExtractedData,
    ) -> RuleEvaluationResult:

        if not rule.is_enabled:
            return RuleEvaluationResult(
                rule=rule,
                matched=False,
            )

        rule_type = rule.rule_type.upper()

        if rule_type == "PRICE":
            matched = self._evaluate_price(
                rule=rule,
                data=data,
            )

        elif rule_type == "AVAILABILITY":
            matched = self._evaluate_availability(
                rule=rule,
                data=data,
            )

        elif rule_type == "KEYWORD":
            matched = self._evaluate_keyword(
                rule=rule,
                data=data,
            )

        else:
            matched = False

        return RuleEvaluationResult(
            rule=rule,
            matched=matched,
        )

    def evaluate_all(
        self,
        rules: list[MonitoringRule],
        data: ExtractedData,
    ) -> list[RuleEvaluationResult]:

        return [
            self.evaluate(
                rule=rule,
                data=data,
            )
            for rule in rules
        ]

    def _evaluate_price(
        self,
        rule: MonitoringRule,
        data: ExtractedData,
    ) -> bool:

        if data.price is None:
            return False

        try:
            current_price = float(data.price)
            target_price = float(rule.target_value)
        except (TypeError, ValueError):
            return False

        operators = {
            "<": lambda: current_price < target_price,
            "<=": lambda: current_price <= target_price,
            "==": lambda: current_price == target_price,
            ">=": lambda: current_price >= target_price,
            ">": lambda: current_price > target_price,
        }

        evaluator = operators.get(
            rule.operator
        )

        if evaluator is None:
            return False

        return evaluator()

    def _evaluate_availability(
        self,
        rule: MonitoringRule,
        data: ExtractedData,
    ) -> bool:

        if data.availability is None:
            return False

        current_status = data.availability.upper()
        target_status = rule.target_value.upper()

        if rule.operator == "==":
            return current_status == target_status

        if rule.operator == "!=":
            return current_status != target_status

        return False

    def _evaluate_keyword(
        self,
        rule: MonitoringRule,
        data: ExtractedData,
    ) -> bool:

        if data.text is None:
            return False

        target = rule.target_value

        if rule.operator == "CONTAINS":
            return target.lower() in data.text.lower()

        if rule.operator == "NOT_CONTAINS":
            return target.lower() not in data.text.lower()

        return False