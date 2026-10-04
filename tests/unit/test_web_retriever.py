
from unittest.mock import Mock

import pytest

from app.monitoring.retriever import (
    PageAccessBlockedError,
    WebRetriever,
)


def make_response(html: str, status_code: int = 200, url: str = "https://example.com/product"):
    response = Mock()
    response.status_code = status_code
    response.text = html
    response.url = url
    response.raise_for_status.return_value = None
    return response


def test_retrieve_returns_normal_product_page(monkeypatch):
    html = """
    <html>
      <head><title>Example Product</title></head>
      <body>
        <h1>Wireless Mouse</h1>
        <span class="price">₹5,499</span>
        <p>In stock</p>
      </body>
    </html>
    """
    monkeypatch.setattr(
        "app.monitoring.retriever.httpx.get",
        lambda *args, **kwargs: make_response(html),
    )

    result = WebRetriever().retrieve("https://example.com/product")

    assert result.status_code == 200
    assert result.url == "https://example.com/product"
    assert "Wireless Mouse" in result.html


@pytest.mark.parametrize(
    "marker",
    [
        "Automated access",
        "Robot check",
        "validateCaptcha",
        "Unusual traffic",
        "Verify you are human",
        "Access denied",
    ],
)
def test_retrieve_rejects_access_challenge(monkeypatch, marker):
    html = f"<html><head><title>Amazon.in</title></head><body>{marker}</body></html>"
    monkeypatch.setattr(
        "app.monitoring.retriever.httpx.get",
        lambda *args, **kwargs: make_response(html),
    )

    with pytest.raises(PageAccessBlockedError):
        WebRetriever().retrieve("https://www.amazon.in/dp/example")


def test_retrieve_still_raises_http_errors(monkeypatch):
    response = make_response("<html>Not found</html>", status_code=404)
    response.raise_for_status.side_effect = RuntimeError("HTTP error")

    monkeypatch.setattr(
        "app.monitoring.retriever.httpx.get",
        lambda *args, **kwargs: response,
    )

    with pytest.raises(RuntimeError, match="HTTP error"):
        WebRetriever().retrieve("https://example.com/missing")
