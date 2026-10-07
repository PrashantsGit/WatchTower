from unittest.mock import Mock

import pytest

from app.monitoring.engine import MonitoringEngineService
from app.monitoring.extractor import ExtractedData
from app.models.monitoring_rule import MonitoringRule


def make_rule(rule_type: str) -> MonitoringRule:
    return MonitoringRule(
        task_id=1,
        rule_type=rule_type,
        operator="==",
        target_value="test",
        is_enabled=True,
    )


class TestMonitoringEngineExtractionValidation:

    def test_price_rule_requires_extracted_price(self):
        rules = [make_rule("PRICE")]
        data = ExtractedData(price=None)

        with pytest.raises(ValueError, match="price"):
            MonitoringEngineService._validate_extracted_data(
                rules=rules,
                data=data,
            )

    def test_price_rule_accepts_extracted_price(self):
        rules = [make_rule("PRICE")]
        data = ExtractedData(price="£51.77")

        MonitoringEngineService._validate_extracted_data(
            rules=rules,
            data=data,
        )

    def test_availability_rule_requires_extracted_availability(self):
        rules = [make_rule("AVAILABILITY")]
        data = ExtractedData(availability=None)

        with pytest.raises(ValueError, match="availability"):
            MonitoringEngineService._validate_extracted_data(
                rules=rules,
                data=data,
            )

    def test_availability_rule_accepts_extracted_availability(self):
        rules = [make_rule("AVAILABILITY")]
        data = ExtractedData(availability="IN_STOCK")

        MonitoringEngineService._validate_extracted_data(
            rules=rules,
            data=data,
        )

    def test_keyword_rule_requires_extracted_text(self):
        rules = [make_rule("KEYWORD")]
        data = ExtractedData(text=None)

        with pytest.raises(ValueError, match="text"):
            MonitoringEngineService._validate_extracted_data(
                rules=rules,
                data=data,
            )

    def test_keyword_rule_accepts_extracted_text(self):
        rules = [make_rule("KEYWORD")]
        data = ExtractedData(text="Product is available")

        MonitoringEngineService._validate_extracted_data(
            rules=rules,
            data=data,
        )

    def test_valid_extracted_value_does_not_depend_on_rule_match(self):
        rules = [
            MonitoringRule(
                task_id=1,
                rule_type="PRICE",
                operator="<",
                target_value="50",
                is_enabled=True,
            )
        ]
        data = ExtractedData(price="£51.77")

        # The price is successfully extracted even though
        # it does not satisfy the monitoring rule.
        MonitoringEngineService._validate_extracted_data(
            rules=rules,
            data=data,
        )

    def test_disabled_rule_does_not_require_extracted_value(self):
        rule = MonitoringRule(
            task_id=1,
            rule_type="PRICE",
            operator="<",
            target_value="50",
            is_enabled=False,
        )
        data = ExtractedData(price=None)

        MonitoringEngineService._validate_extracted_data(
            rules=[rule],
            data=data,
        )

    def test_multiple_rules_require_all_enabled_data(self):
        rules = [
            make_rule("PRICE"),
            make_rule("AVAILABILITY"),
        ]
        data = ExtractedData(
            price="£51.77",
            availability=None,
        )

        with pytest.raises(ValueError, match="availability"):
            MonitoringEngineService._validate_extracted_data(
                rules=rules,
                data=data,
            )