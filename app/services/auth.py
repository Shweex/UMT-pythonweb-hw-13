"""Authentication helpers: password hashing and JWT token management."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a plain-text password for secure storage."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str) -> str:
    """Create a short-lived JWT access token for the given subject."""
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.auth_jwt_access_expiration_seconds)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.auth_jwt_secret, algorithm=settings.auth_jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Decode an access token and return the subject or ``None`` on failure."""
    try:
        payload = jwt.decode(token, settings.auth_jwt_secret, algorithms=[settings.auth_jwt_algorithm])
        return payload.get("sub")
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """Create a JWT used to verify a user's email address."""
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.mail_jwt_expiration_seconds)
    payload = {"sub": email, "exp": expire, "type": "email_verification"}
    return jwt.encode(payload, settings.mail_jwt_secret, algorithm=settings.auth_jwt_algorithm)


def decode_email_verification_token(token: str) -> str | None:
    """Decode an email verification token and return the email or ``None``."""
    try:
        payload = jwt.decode(token, settings.mail_jwt_secret, algorithms=[settings.auth_jwt_algorithm])
        if payload.get("type") != "email_verification":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """Create a JWT used to reset a user's password."""
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.password_reset_jwt_expiration_seconds)
    payload = {"sub": email, "exp": expire, "type": "password_reset"}
    return jwt.encode(payload, settings.mail_jwt_secret, algorithm=settings.auth_jwt_algorithm)


def decode_password_reset_token(token: str) -> str | None:
    """Decode a password reset token and return the email or ``None``."""
    try:
        payload = jwt.decode(token, settings.mail_jwt_secret, algorithms=[settings.auth_jwt_algorithm])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
