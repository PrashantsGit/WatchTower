
import pytest
from bs4 import BeautifulSoup

from app.monitoring.extractor import MonitoringExtractor


@pytest.fixture
def extractor():
    return MonitoringExtractor()


def extract_availability(extractor, html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    return extractor._extract_availability(soup)


def test_extracts_in_stock_from_product_availability_element(extractor):
    html = """
    <html>
        <body>
            <div id="product">
                <p class="availability">
                    <i class="icon-ok"></i>
                    In stock (22 available)
                </p>
            </div>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result == "IN_STOCK"


def test_extracts_out_of_stock_from_product_availability_element(extractor):
    html = """
    <html>
        <body>
            <div id="product">
                <p class="availability">Out of stock</p>
            </div>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result == "OUT_OF_STOCK"


def test_uses_structured_schema_org_availability(extractor):
    html = """
    <html>
        <body>
            <div itemscope itemtype="https://schema.org/Product">
                <link itemprop="availability"
                      href="https://schema.org/InStock">
            </div>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result == "IN_STOCK"


def test_uses_structured_schema_org_out_of_stock(extractor):
    html = """
    <html>
        <body>
            <div itemscope itemtype="https://schema.org/Product">
                <link itemprop="availability"
                      href="https://schema.org/OutOfStock">
            </div>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result == "OUT_OF_STOCK"


def test_ignores_unrelated_unavailable_text_when_product_is_in_stock(extractor):
    html = """
    <html>
        <body>
            <div id="product">
                <p class="availability">In stock (10 available)</p>
            </div>

            <footer>
                <p>Another item is currently unavailable.</p>
            </footer>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result == "IN_STOCK"


def test_does_not_infer_availability_from_unrelated_page_text(extractor):
    html = """
    <html>
        <body>
            <h1>Example Product</h1>
            <p>Some other products are available.</p>
            <footer>
                <p>This service is currently unavailable in some regions.</p>
            </footer>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result is None


def test_returns_none_when_availability_is_unknown(extractor):
    html = """
    <html>
        <body>
            <h1>Example Product</h1>
            <p>Price: £51.77</p>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result is None


def test_product_availability_takes_precedence_over_unrelated_page_text(extractor):
    html = """
    <html>
        <body>
            <div id="product">
                <p class="availability">Out of stock</p>
            </div>

            <div class="recommendations">
                <p>Recommended products available now.</p>
            </div>
        </body>
    </html>
    """

    result = extract_availability(extractor, html)

    assert result == "OUT_OF_STOCK"
