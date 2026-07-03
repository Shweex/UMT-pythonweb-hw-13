"""Unit tests for email delivery helpers."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.email import send_password_reset_email, send_verification_email


@pytest.mark.asyncio
@patch("app.services.email.FastMail.send_message", new_callable=AsyncMock)
async def test_send_verification_email(mock_send):
    await send_verification_email("user@test.com", "token123", "http://testserver")
    mock_send.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.email.FastMail.send_message", new_callable=AsyncMock)
async def test_send_password_reset_email(mock_send):
    await send_password_reset_email("user@test.com", "token123", "http://testserver")
    mock_send.assert_awaited_once()
