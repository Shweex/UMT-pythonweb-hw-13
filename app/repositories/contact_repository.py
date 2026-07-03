"""Repository for contact persistence operations."""

import uuid
from datetime import date, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Contact


class ContactRepository:
    """Encapsulates database access for :class:`~app.models.contact.Contact` records."""

    def __init__(self, db: Session) -> None:
        """Initialize the repository with an active database session.

        Args:
            db: SQLAlchemy session bound to the current request or test.
        """
        self.db = db

    def create(self, contact: Contact) -> Contact:
        """Persist a new contact and refresh the instance from the database."""
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_by_id_for_owner(self, contact_id: uuid.UUID, owner_id: uuid.UUID) -> Contact | None:
        """Return a contact owned by the given user or ``None`` if not found."""
        return (
            self.db.query(Contact)
            .filter(Contact.id == contact_id, Contact.owner_id == owner_id)
            .first()
        )

    def list_for_owner(self, owner_id: uuid.UUID) -> list[Contact]:
        """Return all contacts for the given owner ordered by creation time."""
        return (
            self.db.query(Contact)
            .filter(Contact.owner_id == owner_id)
            .order_by(Contact.created_at.desc())
            .all()
        )

    def search_for_owner(self, owner_id: uuid.UUID, query: str) -> list[Contact]:
        """Search contacts by first name, last name, or email for the given owner."""
        search_pattern = f"%{query}%"
        return (
            self.db.query(Contact)
            .filter(
                Contact.owner_id == owner_id,
                or_(
                    Contact.first_name.ilike(search_pattern),
                    Contact.last_name.ilike(search_pattern),
                    Contact.email.ilike(search_pattern),
                ),
            )
            .all()
        )

    def upcoming_birthdays_for_owner(self, owner_id: uuid.UUID, days: int = 7) -> list[Contact]:
        """Return contacts with birthdays within the next ``days`` days."""
        today = date.today()
        contacts = self.db.query(Contact).filter(Contact.owner_id == owner_id).all()
        upcoming: list[Contact] = []

        for contact in contacts:
            birthday_this_year = contact.birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if birthday_this_year <= today + timedelta(days=days):
                upcoming.append(contact)

        upcoming.sort(key=lambda contact: contact.birthday.replace(year=today.year))
        return upcoming

    def update(self, contact: Contact) -> Contact:
        """Commit pending changes for an existing contact."""
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete(self, contact: Contact) -> None:
        """Remove a contact from the database."""
        self.db.delete(contact)
        self.db.commit()
