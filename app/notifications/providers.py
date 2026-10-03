
import json
import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

from pywebpush import WebPushException, webpush

from app.core.config import Settings, settings


logger = logging.getLogger(__name__)


class NotificationProvider(Protocol):
    """Contract implemented by email notification providers."""

    def send(
        self,
        *,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> None:
        """Send a notification or raise an exception on failure."""
        ...


class SMTPEmailProvider:
    """Deliver email notifications using an SMTP server."""

    def __init__(
        self,
        configuration: Settings | None = None,
    ):
        self.configuration = configuration or settings

    def send(
        self,
        *,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> None:
        config = self.configuration

        if not config.smtp_host:
            raise RuntimeError("SMTP_HOST is not configured.")

        if not config.smtp_from_email:
            raise RuntimeError("SMTP_FROM_EMAIL is not configured.")

        if config.smtp_username and not config.smtp_password:
            raise RuntimeError(
                "SMTP_PASSWORD is required when SMTP_USERNAME is set."
            )

        message = EmailMessage()
        message["From"] = config.smtp_from_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(
            host=config.smtp_host,
            port=config.smtp_port,
            timeout=config.smtp_timeout_seconds,
        ) as server:
            if config.smtp_use_tls:
                server.starttls()

            if config.smtp_username:
                server.login(
                    config.smtp_username,
                    config.smtp_password,
                )

            server.send_message(message)

        logger.info("Email notification sent to %s", recipient_email)


class ExpiredPushSubscriptionError(Exception):
    """Raised when a push service reports that a subscription is expired."""


class WebPushProvider:
    """Deliver browser push notifications using the Web Push protocol."""

    def __init__(
        self,
        configuration: Settings | None = None,
    ):
        self.configuration = configuration or settings

    def send(
        self,
        *,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        title: str,
        body: str,
        target_url: str | None = None,
    ) -> None:
        config = self.configuration

        if not config.vapid_private_key:
            raise RuntimeError("VAPID_PRIVATE_KEY is not configured.")

        if not config.vapid_subject:
            raise RuntimeError("VAPID_SUBJECT is not configured.")

        if not endpoint or not p256dh_key or not auth_key:
            raise ValueError(
                "Push endpoint and subscription keys are required."
            )

        payload = {
            "title": title,
            "body": body,
            "url": target_url,
        }

        subscription_info = {
            "endpoint": endpoint,
            "keys": {
                "p256dh": p256dh_key,
                "auth": auth_key,
            },
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=config.vapid_private_key,
                vapid_claims={"sub": config.vapid_subject},
                ttl=config.webpush_ttl_seconds,
            )
        except WebPushException as exc:
            response = getattr(exc, "response", None)
            status_code = getattr(response, "status_code", None)

            if status_code in (404, 410):
                raise ExpiredPushSubscriptionError(
                    "The browser push subscription is no longer valid."
                ) from exc

            # Preserve other failures for the delivery service to handle.
            raise

        logger.info("Browser push notification sent successfully.")
