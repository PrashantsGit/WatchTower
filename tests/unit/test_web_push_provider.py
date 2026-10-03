
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from pywebpush import WebPushException

from app.core.config import Settings
from app.notifications.providers import (
    ExpiredPushSubscriptionError,
    WebPushProvider,
)


@pytest.fixture
def configuration():
    return Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        secret_key="test-secret",
        vapid_private_key="tests/fixtures/vapid_private.pem",
        vapid_public_key="test-public-key",
        vapid_subject="mailto:test@example.com",
        webpush_ttl_seconds=1800,
    )


@pytest.fixture
def provider(configuration):
    return WebPushProvider(configuration=configuration)


def test_send_calls_webpush_with_subscription_and_payload(provider):
    with patch("app.notifications.providers.webpush") as mock_webpush:
        provider.send(
            endpoint="https://push.example.test/subscription",
            p256dh_key="test-p256dh",
            auth_key="test-auth",
            title="Price dropped",
            body="The monitored price changed.",
            target_url="https://example.com/product",
        )

    mock_webpush.assert_called_once()
    kwargs = mock_webpush.call_args.kwargs

    assert kwargs["subscription_info"] == {
        "endpoint": "https://push.example.test/subscription",
        "keys": {
            "p256dh": "test-p256dh",
            "auth": "test-auth",
        },
    }
    assert kwargs["vapid_private_key"] == "tests/fixtures/vapid_private.pem"
    assert kwargs["vapid_claims"] == {"sub": "mailto:test@example.com"}
    assert kwargs["ttl"] == 1800
    assert '"title": "Price dropped"' in kwargs["data"]
    assert '"url": "https://example.com/product"' in kwargs["data"]


def test_send_rejects_missing_private_key(configuration):
    configuration.vapid_private_key = None
    provider = WebPushProvider(configuration=configuration)

    with pytest.raises(RuntimeError, match="VAPID_PRIVATE_KEY"):
        provider.send(
            endpoint="https://push.example.test/subscription",
            p256dh_key="test-p256dh",
            auth_key="test-auth",
            title="Test",
            body="Test message",
        )


def test_send_rejects_missing_subject(configuration):
    configuration.vapid_subject = None
    provider = WebPushProvider(configuration=configuration)

    with pytest.raises(RuntimeError, match="VAPID_SUBJECT"):
        provider.send(
            endpoint="https://push.example.test/subscription",
            p256dh_key="test-p256dh",
            auth_key="test-auth",
            title="Test",
            body="Test message",
        )


def test_send_rejects_missing_subscription_keys(provider):
    with pytest.raises(ValueError, match="subscription keys"):
        provider.send(
            endpoint="https://push.example.test/subscription",
            p256dh_key="",
            auth_key="test-auth",
            title="Test",
            body="Test message",
        )


@pytest.mark.parametrize("status_code", [404, 410])
def test_send_identifies_expired_subscription(provider, status_code):
    response = SimpleNamespace(status_code=status_code)
    error = WebPushException(
        "Subscription expired",
        response=response,
    )

    with patch(
        "app.notifications.providers.webpush",
        side_effect=error,
    ):
        with pytest.raises(ExpiredPushSubscriptionError):
            provider.send(
                endpoint="https://push.example.test/subscription",
                p256dh_key="test-p256dh",
                auth_key="test-auth",
                title="Test",
                body="Test message",
            )


def test_send_propagates_temporary_failure(provider):
    response = SimpleNamespace(status_code=503)
    error = WebPushException(
        "Push service temporarily unavailable",
        response=response,
    )

    with patch(
        "app.notifications.providers.webpush",
        side_effect=error,
    ):
        with pytest.raises(WebPushException):
            provider.send(
                endpoint="https://push.example.test/subscription",
                p256dh_key="test-p256dh",
                auth_key="test-auth",
                title="Test",
                body="Test message",
            )
