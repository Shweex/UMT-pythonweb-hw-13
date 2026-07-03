"""Pydantic schemas for user-related API payloads."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Payload for registering a new user."""

    email: EmailStr
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Payload for authenticating an existing user."""

    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    """Public representation of a user returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    is_verified: bool
    role: UserRole
    avatar_url: str | None
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT access token returned after successful login."""

    access_token: str
    token_type: str = "bearer"


class EmailVerificationResponse(BaseModel):
    """Response returned after email verification."""

    message: str
    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Payload for initiating a password reset flow."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Payload for confirming a password reset with a new password."""

    new_password: str = Field(min_length=6, max_length=128)


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
