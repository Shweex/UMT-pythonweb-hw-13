"""Pydantic schemas for contact-related API payloads."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    """Payload for creating a new contact."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=50)
    birthday: date
    additional_data: str | None = None


class ContactUpdate(BaseModel):
    """Payload for partially updating an existing contact."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=50)
    birthday: date | None = None
    additional_data: str | None = None


class ContactResponse(BaseModel):
    """Public representation of a contact returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: str | None
    created_at: datetime
    updated_at: datetime
