
import pytest
from pydantic import ValidationError

from app.schemas.browser_push_subscription import (
    RegisterBrowserPushSubscriptionRequest,
)


def test_subscription_request_accepts_browser_payload():
    request = RegisterBrowserPushSubscriptionRequest.model_validate(
        {
            "endpoint": "https://push.example.test/subscription/123",
            "expirationTime": None,
            "keys": {
                "p256dh": "test-public-key",
                "auth": "test-auth-key",
            },
        }
    )

    assert request.endpoint == (
        "https://push.example.test/subscription/123"
    )
    assert request.keys.p256dh == "test-public-key"
    assert request.keys.auth == "test-auth-key"
    assert request.expiration_time is None


def test_subscription_request_accepts_snake_case_expiration_time():
    request = RegisterBrowserPushSubscriptionRequest.model_validate(
        {
            "endpoint": "https://push.example.test/subscription/123",
            "expiration_time": "2026-10-04T10:00:00Z",
            "keys": {
                "p256dh": "test-public-key",
                "auth": "test-auth-key",
            },
        }
    )

    assert request.expiration_time is not None


def test_subscription_request_rejects_missing_keys():
    with pytest.raises(ValidationError):
        RegisterBrowserPushSubscriptionRequest.model_validate(
            {
                "endpoint": "https://push.example.test/subscription/123",
                "keys": {
                    "p256dh": "",
                    "auth": "test-auth-key",
                },
            }
        )
