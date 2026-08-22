from unittest.mock import Mock, patch

import pytest

from app.monitoring.retriever import RetrievedPage, WebRetriever


def test_retrieve_returns_page():
    retriever = WebRetriever()

    mock_response = Mock()
    mock_response.url = "https://example.com"
    mock_response.status_code = 200
    mock_response.text = "<html><body>Hello</body></html>"

    with patch(
        "app.monitoring.retriever.httpx.get",
        return_value=mock_response,
    ) as mock_get:

        result = retriever.retrieve(
            "https://example.com"
        )

    mock_get.assert_called_once_with(
        "https://example.com",
        timeout=30.0,
        follow_redirects=True,
    )

    mock_response.raise_for_status.assert_called_once()

    assert isinstance(result, RetrievedPage)
    assert result.url == "https://example.com"
    assert result.status_code == 200
    assert result.html == "<html><body>Hello</body></html>"


def test_retrieve_follows_redirect():
    retriever = WebRetriever()

    mock_response = Mock()
    mock_response.url = "https://example.com/final"
    mock_response.status_code = 200
    mock_response.text = "<html>Final page</html>"

    with patch(
        "app.monitoring.retriever.httpx.get",
        return_value=mock_response,
    ):

        result = retriever.retrieve(
            "https://example.com/start"
        )

    assert result.url == "https://example.com/final"


def test_retrieve_raises_http_error():
    retriever = WebRetriever()

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception(
        "HTTP error"
    )

    with patch(
        "app.monitoring.retriever.httpx.get",
        return_value=mock_response,
    ):

        with pytest.raises(
            Exception,
            match="HTTP error",
        ):
            retriever.retrieve(
                "https://example.com"
            )


def test_retriever_uses_custom_timeout():
    retriever = WebRetriever(timeout=10.0)

    mock_response = Mock()
    mock_response.url = "https://example.com"
    mock_response.status_code = 200
    mock_response.text = "<html></html>"

    with patch(
        "app.monitoring.retriever.httpx.get",
        return_value=mock_response,
    ) as mock_get:

        retriever.retrieve(
            "https://example.com"
        )

    mock_get.assert_called_once_with(
        "https://example.com",
        timeout=10.0,
        follow_redirects=True,
    )