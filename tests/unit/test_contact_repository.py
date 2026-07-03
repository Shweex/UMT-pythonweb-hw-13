"""Unit tests for :mod:`app.repositories.contact_repository`."""

import uuid
from datetime import date, timedelta

from app.models import Contact
from app.repositories import ContactRepository


def test_create_and_get_by_id_for_owner(db_session, regular_user):
    repo = ContactRepository(db_session)
    contact = Contact(
        owner_id=regular_user.id,
        first_name="Anna",
        last_name="Smith",
        email="anna@example.com",
        phone="+380501111111",
        birthday=date(1995, 1, 1),
    )
    created = repo.create(contact)
    found = repo.get_by_id_for_owner(created.id, regular_user.id)
    assert found is not None
    assert found.first_name == "Anna"


def test_get_by_id_for_owner_returns_none_for_other_user(db_session, regular_user, admin_user):
    repo = ContactRepository(db_session)
    contact = Contact(
        owner_id=regular_user.id,
        first_name="Private",
        last_name="Contact",
        email="private@example.com",
        phone="+380502222222",
        birthday=date(1992, 2, 2),
    )
    created = repo.create(contact)
    assert repo.get_by_id_for_owner(created.id, admin_user.id) is None


def test_list_for_owner(db_session, regular_user, sample_contact):
    repo = ContactRepository(db_session)
    contacts = repo.list_for_owner(regular_user.id)
    assert len(contacts) == 1
    assert contacts[0].id == sample_contact.id


def test_search_for_owner(db_session, regular_user, sample_contact):
    repo = ContactRepository(db_session)
    results = repo.search_for_owner(regular_user.id, "John")
    assert len(results) == 1
    assert results[0].id == sample_contact.id


def test_search_for_owner_no_match(db_session, regular_user, sample_contact):
    repo = ContactRepository(db_session)
    results = repo.search_for_owner(regular_user.id, "Missing")
    assert results == []


def test_upcoming_birthdays_for_owner(db_session, regular_user):
    repo = ContactRepository(db_session)
    today = date.today()
    soon = today + timedelta(days=3)
    contact = Contact(
        owner_id=regular_user.id,
        first_name="Birthday",
        last_name="Soon",
        email="birthday@example.com",
        phone="+380503333333",
        birthday=date(2000, soon.month, soon.day),
    )
    repo.create(contact)
    upcoming = repo.upcoming_birthdays_for_owner(regular_user.id)
    assert len(upcoming) == 1


def test_update_and_delete(db_session, regular_user, sample_contact):
    repo = ContactRepository(db_session)
    sample_contact.first_name = "Updated"
    updated = repo.update(sample_contact)
    assert updated.first_name == "Updated"

    contact_id = updated.id
    repo.delete(updated)
    assert repo.get_by_id_for_owner(contact_id, regular_user.id) is None


def test_get_by_id_for_owner_missing(db_session, regular_user):
    repo = ContactRepository(db_session)
    assert repo.get_by_id_for_owner(uuid.uuid4(), regular_user.id) is None
