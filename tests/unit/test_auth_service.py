"""Unit tests for authentication helpers."""

from app.services.auth import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_access_token,
    decode_email_verification_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token("user-123")
    assert decode_access_token(token) == "user-123"
    assert decode_access_token("invalid.token.value") is None


def test_email_verification_token_roundtrip():
    token = create_email_verification_token("user@test.com")
    assert decode_email_verification_token(token) == "user@test.com"
    assert decode_email_verification_token(create_access_token("user-123")) is None


def test_password_reset_token_roundtrip():
    token = create_password_reset_token("user@test.com")
    assert decode_password_reset_token(token) == "user@test.com"
    assert decode_password_reset_token(create_access_token("user-123")) is None
