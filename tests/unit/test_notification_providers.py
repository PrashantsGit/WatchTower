from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.notifications.providers import SMTPEmailProvider


def make_configuration(**overrides):
    values = {
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_username": "watchtower@example.com",
        "smtp_password": "test-password",
        "smtp_from_email": "watchtower@example.com",
        "smtp_use_tls": True,
        "smtp_timeout_seconds": 10.0,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@patch("app.notifications.providers.smtplib.SMTP")
def test_smtp_provider_sends_email(mock_smtp):
    server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = server

    provider = SMTPEmailProvider(
        configuration=make_configuration(),
    )

    provider.send(
        recipient_email="recipient@example.com",
        subject="WatchTower alert",
        body="The price has changed.",
    )

    mock_smtp.assert_called_once_with(
        host="smtp.example.com",
        port=587,
        timeout=10.0,
    )
    server.starttls.assert_called_once_with()
    server.login.assert_called_once_with(
        "watchtower@example.com",
        "test-password",
    )
    server.send_message.assert_called_once()

    message = server.send_message.call_args.args[0]

    assert message["To"] == "recipient@example.com"
    assert message["From"] == "watchtower@example.com"
    assert message["Subject"] == "WatchTower alert"
    assert message.get_content().strip() == (
        "The price has changed."
    )


@patch("app.notifications.providers.smtplib.SMTP")
def test_smtp_provider_skips_tls_when_disabled(mock_smtp):
    server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = server

    provider = SMTPEmailProvider(
        configuration=make_configuration(
            smtp_use_tls=False,
            smtp_username=None,
            smtp_password=None,
        ),
    )

    provider.send(
        recipient_email="recipient@example.com",
        subject="Test",
        body="Test message",
    )

    server.starttls.assert_not_called()
    server.login.assert_not_called()
    server.send_message.assert_called_once()


@patch("app.notifications.providers.smtplib.SMTP")
def test_smtp_provider_requires_host(mock_smtp):
    provider = SMTPEmailProvider(
        configuration=make_configuration(
            smtp_host=None,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="SMTP_HOST is not configured",
    ):
        provider.send(
            recipient_email="recipient@example.com",
            subject="Test",
            body="Test message",
        )

    mock_smtp.assert_not_called()


@patch("app.notifications.providers.smtplib.SMTP")
def test_smtp_provider_requires_sender(mock_smtp):
    provider = SMTPEmailProvider(
        configuration=make_configuration(
            smtp_from_email=None,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="SMTP_FROM_EMAIL is not configured",
    ):
        provider.send(
            recipient_email="recipient@example.com",
            subject="Test",
            body="Test message",
        )

    mock_smtp.assert_not_called()


@patch("app.notifications.providers.smtplib.SMTP")
def test_smtp_provider_requires_password_when_username_is_set(
    mock_smtp,
):
    provider = SMTPEmailProvider(
        configuration=make_configuration(
            smtp_password=None,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="SMTP_PASSWORD is required",
    ):
        provider.send(
            recipient_email="recipient@example.com",
            subject="Test",
            body="Test message",
        )

    mock_smtp.assert_not_called()