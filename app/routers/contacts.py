"""Contact management routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Contact, User
from app.repositories import ContactRepository
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


def _get_user_contact(contact_id: UUID, user: User, contact_repo: ContactRepository) -> Contact:
    """Return a contact owned by the user or raise HTTP 404."""
    contact = contact_repo.get_by_id_for_owner(contact_id, user.id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new contact for the authenticated user."""
    contact_repo = ContactRepository(db)
    contact = Contact(owner_id=current_user.id, **payload.model_dump())
    return contact_repo.create(contact)


@router.get("", response_model=list[ContactResponse])
def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all contacts belonging to the authenticated user."""
    contact_repo = ContactRepository(db)
    return contact_repo.list_for_owner(current_user.id)


@router.get("/search", response_model=list[ContactResponse])
def search_contacts(
    query: str = Query(min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search contacts by first name, last name, or email."""
    contact_repo = ContactRepository(db)
    return contact_repo.search_for_owner(current_user.id, query)


@router.get("/upcoming-birthdays", response_model=list[ContactResponse])
def upcoming_birthdays(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return contacts with birthdays within the next seven days."""
    contact_repo = ContactRepository(db)
    return contact_repo.upcoming_birthdays_for_owner(current_user.id)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a single contact by identifier."""
    contact_repo = ContactRepository(db)
    return _get_user_contact(contact_id, current_user, contact_repo)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: UUID,
    payload: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing contact owned by the authenticated user."""
    contact_repo = ContactRepository(db)
    contact = _get_user_contact(contact_id, current_user, contact_repo)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    return contact_repo.update(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a contact owned by the authenticated user."""
    contact_repo = ContactRepository(db)
    contact = _get_user_contact(contact_id, current_user, contact_repo)
    contact_repo.delete(contact)
