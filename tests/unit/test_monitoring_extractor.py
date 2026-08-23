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


def test_extract_price_from_visible_text():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <h1>Test Product</h1>
                    <div>Price: ₹49,999</div>
                </body>
            </html>
        """,
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

    assert result.price == "₹49,999"


def test_extract_availability_in_stock():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <button>Add to Cart</button>
                    <span>In Stock</span>
                </body>
            </html>
        """,
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

    assert result.availability == "IN_STOCK"


def test_extract_availability_out_of_stock():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <button disabled>Out of Stock</button>
                </body>
            </html>
        """,
    )

    rule = MonitoringRule(
        task_id=1,
        rule_type="AVAILABILITY",
        operator="==",
        target_value="OUT_OF_STOCK",
        is_enabled=True,
    )

    result = extractor.extract(
        page=page,
        rules=[rule],
    )

    assert result.availability == "OUT_OF_STOCK"


def test_extract_availability_returns_none_when_status_unknown():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <h1>Test Product</h1>
                    <p>Great product with fast delivery.</p>
                </body>
            </html>
        """,
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

def test_extract_price_from_itemprop():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <span itemprop="price" content="49999">
                        ₹49,999
                    </span>
                </body>
            </html>
        """,
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

    assert result.price == "49999"


def test_extract_price_from_json_ld():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <head>
                    <script type="application/ld+json">
                    {
                        "@context": "https://schema.org",
                        "@type": "Product",
                        "name": "Test Product",
                        "offers": {
                            "@type": "Offer",
                            "price": "49999",
                            "priceCurrency": "INR"
                        }
                    }
                    </script>
                </head>
            </html>
        """,
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

    assert result.price == "49999"


def test_extract_price_from_meta():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <head>
                    <meta
                        property="product:price:amount"
                        content="49999"
                    >
                </head>
            </html>
        """,
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

    assert result.price == "49999"


def test_extract_price_from_price_class():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <div class="product-price">
                        ₹49,999
                    </div>
                </body>
            </html>
        """,
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

    assert result.price == "₹49,999"


def test_extract_price_returns_none_when_price_missing():
    extractor = MonitoringExtractor()

    page = RetrievedPage(
        url="https://example.com",
        status_code=200,
        html="""
            <html>
                <body>
                    <h1>Test Product</h1>
                    <p>Rated 4.5 out of 5</p>
                    <p>128 reviews</p>
                </body>
            </html>
        """,
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