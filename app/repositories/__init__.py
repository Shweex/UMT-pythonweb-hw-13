"""Data access layer for the application."""

from app.repositories.contact_repository import ContactRepository
from app.repositories.user_repository import UserRepository

__all__ = ["ContactRepository", "UserRepository"]
