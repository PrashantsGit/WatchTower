
from bs4 import BeautifulSoup

from app.monitoring.extractor import MonitoringExtractor


def test_extracts_clean_amazon_offscreen_price():
    html = """
    <div id="corePrice_feature_div">
        <span class="a-price">
            <span class="a-offscreen">₹5,499.00</span>
            <span class="a-price-symbol">₹</span>
            <span class="a-price-whole">5,499</span>
            <span class="a-price-decimal">.</span>
            <span class="a-price-fraction">00</span>
        </span>
    </div>
    """

    extractor = MonitoringExtractor()
    soup = BeautifulSoup(html, "html.parser")

    result = extractor._extract_price(soup)

    assert result == "₹5,499.00"


def test_amazon_price_selector_ignores_duplicate_container_text():
    html = """
    <div id="corePrice_feature_div">
        ₹5,499.00 ₹ 5,499 . 00
        <span class="a-price">
            <span class="a-offscreen">₹5,499.00</span>
        </span>
    </div>
    """

    extractor = MonitoringExtractor()
    soup = BeautifulSoup(html, "html.parser")

    result = extractor._extract_price(soup)

    assert result == "₹5,499.00"
