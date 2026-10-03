from app.models.monitoring_rule import MonitoringRule
from app.monitoring.evaluator import (
    MonitoringRuleEvaluator,
    RuleEvaluationResult,
)
from app.monitoring.extractor import ExtractedData


def create_rule(
    rule_type: str,
    operator: str,
    target_value: str,
    is_enabled: bool = True,
) -> MonitoringRule:

    return MonitoringRule(
        task_id=1,
        rule_type=rule_type,
        operator=operator,
        target_value=target_value,
        is_enabled=is_enabled,
    )


def test_price_rule_less_than_matches():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    data = ExtractedData(
        price="45000",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert isinstance(
        result,
        RuleEvaluationResult,
    )

    assert result.matched is True


def test_price_rule_less_than_does_not_match():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    data = ExtractedData(
        price="55000",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is False


def test_price_rule_equal_matches():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="==",
        target_value="50000",
    )

    data = ExtractedData(
        price="50000",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is True


def test_price_rule_greater_than_or_equal_matches():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator=">=",
        target_value="50000",
    )

    data = ExtractedData(
        price="50000",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is True


def test_price_rule_handles_missing_price():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    data = ExtractedData(
        price=None,
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is False


def test_price_rule_handles_invalid_price():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    data = ExtractedData(
        price="not-a-price",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is False


def test_availability_equal_matches():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="AVAILABILITY",
        operator="==",
        target_value="IN_STOCK",
    )

    data = ExtractedData(
        availability="IN_STOCK",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is True


def test_availability_not_equal_matches():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="AVAILABILITY",
        operator="!=",
        target_value="OUT_OF_STOCK",
    )

    data = ExtractedData(
        availability="IN_STOCK",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is True


def test_availability_handles_missing_status():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="AVAILABILITY",
        operator="==",
        target_value="IN_STOCK",
    )

    data = ExtractedData(
        availability=None,
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is False


def test_keyword_contains_matches_case_insensitive():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
    )

    data = ExtractedData(
        text="The admissions open for the new academic session.",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is True


def test_keyword_contains_does_not_match():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
    )

    data = ExtractedData(
        text="Applications are currently closed.",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is False


def test_keyword_not_contains_matches():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="KEYWORD",
        operator="NOT_CONTAINS",
        target_value="Sold Out",
    )

    data = ExtractedData(
        text="Tickets are available now.",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is True


def test_keyword_handles_missing_text():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
    )

    data = ExtractedData(
        text=None,
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is False


def test_disabled_rule_does_not_match():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
        is_enabled=False,
    )

    data = ExtractedData(
        text="Admissions Open",
    )

    result = evaluator.evaluate(
        rule=rule,
        data=data,
    )

    assert result.matched is False


def test_evaluate_all_returns_results_for_all_rules():
    evaluator = MonitoringRuleEvaluator()

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

    data = ExtractedData(
        price="45000",
        text="Admissions Open",
    )

    results = evaluator.evaluate_all(
        rules=[
            price_rule,
            keyword_rule,
        ],
        data=data,
    )

    assert len(results) == 2
    assert results[0].matched is True
    assert results[1].matched is True


def test_price_rule_handles_currency_symbol():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="60",
    )

    data = ExtractedData(price="£51.77")

    result = evaluator.evaluate(rule=rule, data=data)

    assert result.matched is True


def test_price_rule_handles_comma_separators():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="<=",
        target_value="1,300.00",
    )

    data = ExtractedData(price="₹1,299.00")

    result = evaluator.evaluate(rule=rule, data=data)

    assert result.matched is True


def test_price_rule_handles_equal_currency_values():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="==",
        target_value="49.99",
    )

    data = ExtractedData(price="$49.99")

    result = evaluator.evaluate(rule=rule, data=data)

    assert result.matched is True


def test_price_rule_rejects_malformed_price():
    evaluator = MonitoringRuleEvaluator()

    rule = create_rule(
        rule_type="PRICE",
        operator="<",
        target_value="60",
    )

    data = ExtractedData(price="not-a-price")

    result = evaluator.evaluate(rule=rule, data=data)

    assert result.matched is False
