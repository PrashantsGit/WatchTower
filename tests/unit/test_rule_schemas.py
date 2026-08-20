import pytest
from pydantic import ValidationError

from app.schemas.rule import (
    CreateRuleRequest,
    RuleResponse,
    UpdateRuleRequest,
)


def test_create_rule_request():
    request = CreateRuleRequest(
        rule_type="PRICE",
        operator="<",
        target_value="50000",
    )

    assert request.rule_type == "PRICE"
    assert request.operator == "<"
    assert request.target_value == "50000"


def test_update_rule_request():
    request = UpdateRuleRequest(
        rule_type="PRICE",
        operator="<=",
        target_value="45000",
        is_enabled=False,
    )

    assert request.rule_type == "PRICE"
    assert request.operator == "<="
    assert request.target_value == "45000"
    assert request.is_enabled is False


def test_create_rule_request_rejects_empty_values():
    with pytest.raises(ValidationError):
        CreateRuleRequest(
            rule_type="",
            operator="<",
            target_value="50000",
        )

    with pytest.raises(ValidationError):
        CreateRuleRequest(
            rule_type="PRICE",
            operator="",
            target_value="50000",
        )

    with pytest.raises(ValidationError):
        CreateRuleRequest(
            rule_type="PRICE",
            operator="<",
            target_value="",
        )