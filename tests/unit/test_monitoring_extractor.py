from app.models.monitoring_rule import MonitoringRule
from app.monitoring.extractor import (
    ExtractedData,
    MonitoringExtractor,
)
from app.monitoring.retriever import RetrievedPage


def test_extract_keyword_text():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <h1>Admissions Open</h1>
                    <p>Applications are now available.</p>
                </body>
            </html>
        """,
    )

    rule = MonitoringRule(
        task_id=1,
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
        is_enabled=True,
    )

    result = extractor.extract(
        page=page,
        rules=[rule],
    )

    assert isinstance(result, ExtractedData)
    assert result.text is not None
    assert "Admissions Open" in result.text
    assert "Applications are now available." in result.text


def test_extract_ignores_disabled_keyword_rule():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html><body>Admissions Open</body></html>",
    )

    rule = MonitoringRule(
        task_id=1,
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Admissions Open",
        is_enabled=False,
    )

    result = extractor.extract(
        page=page,
        rules=[rule],
    )

    assert result.text is None


def test_extract_only_extracts_required_information():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html><body>Product information</body></html>",
    )

    rule = MonitoringRule(
        task_id=1,
        rule_type="KEYWORD",
        operator="CONTAINS",
        target_value="Product",
        is_enabled=True,
    )

    result = extractor.extract(
        page=page,
        rules=[rule],
    )

    assert result.text is not None
    assert result.price is None
    assert result.availability is None


def test_extract_price_currently_returns_none():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html><body>₹49,999</body></html>",
    )

    rule = MonitoringRule(
        task_id=1,
        rule_type="PRICE",
        operator="<",
        target_value="50000",
        is_enabled=True,
    )

    result = extractor.extract(
        page=page,
        rules=[rule],
    )

    assert result.price is None


def test_extract_availability_currently_returns_none():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="<html><body>In Stock</body></html>",
    )

    rule = MonitoringRule(
        task_id=1,
        rule_type="AVAILABILITY",
        operator="==",
        target_value="IN_STOCK",
        is_enabled=True,
    )

    result = extractor.extract(
        page=page,
        rules=[rule],
    )

    assert result.availability is None