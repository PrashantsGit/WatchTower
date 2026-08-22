from app.models.monitoring_rule import MonitoringRule
from app.monitoring.evaluator import RuleEvaluationResult
from app.monitoring.trigger import MonitoringTriggerService


def create_rule(
    rule_type: str,
    operator: str,
    target_value: str,
) -> MonitoringRule:

    return MonitoringRule(
        task_id=1,
        rule_type=rule_type,
        operator=operator,
        target_value=target_value,
        is_enabled=True,
    )


def test_should_trigger_when_rule_matches():
    service = MonitoringTriggerService()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    evaluations = [
        RuleEvaluationResult(
            rule=rule,
            matched=True,
        )
    ]

    assert service.should_trigger(
        evaluations
    ) is True


def test_should_not_trigger_when_no_rule_matches():
    service = MonitoringTriggerService()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    evaluations = [
        RuleEvaluationResult(
            rule=rule,
            matched=False,
        )
    ]

    assert service.should_trigger(
        evaluations
    ) is False


def test_should_not_trigger_for_empty_evaluations():
    service = MonitoringTriggerService()

    assert service.should_trigger(
        []
    ) is False


def test_get_triggered_rules_returns_only_matched_rules():
    service = MonitoringTriggerService()

    price_rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    keyword_rule = create_rule(
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions",
    )

    evaluations = [
        RuleEvaluationResult(
            rule=price_rule,
            matched=True,
        ),
        RuleEvaluationResult(
            rule=keyword_rule,
            matched=False,
        ),
    ]

    triggered = service.get_triggered_rules(
        evaluations
    )

    assert len(triggered) == 1
    assert triggered[0].rule is price_rule
    assert triggered[0].matched is True


def test_get_triggered_rules_returns_multiple_matches():
    service = MonitoringTriggerService()

    price_rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    availability_rule = create_rule(
        rule_type="AVAILABILITY",
        operator="==",
        target_value="IN_STOCK",
    )

    keyword_rule = create_rule(
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions",
    )

    evaluations = [
        RuleEvaluationResult(
            rule=price_rule,
            matched=True,
        ),
        RuleEvaluationResult(
            rule=availability_rule,
            matched=True,
        ),
        RuleEvaluationResult(
            rule=keyword_rule,
            matched=False,
        ),
    ]

    triggered = service.get_triggered_rules(
        evaluations
    )

    assert len(triggered) == 2

    triggered_rules = {
        evaluation.rule
        for evaluation in triggered
    }

    assert price_rule in triggered_rules
    assert availability_rule in triggered_rules
    assert keyword_rule not in triggered_rules