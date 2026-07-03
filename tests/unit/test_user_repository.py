"""Unit tests for :mod:`app.repositories.user_repository`."""

import uuid

from app.models import User, UserRole
from app.repositories import UserRepository
from app.services.auth import hash_password


def test_create_and_get_by_id(db_session):
    repo = UserRepository(db_session)
    user = User(
        email="repo@test.com",
        username="repouser",
        hashed_password=hash_password("secret123"),
        role=UserRole.USER,
    )
    created = repo.create(user)
    found = repo.get_by_id(created.id)
    assert found is not None
    assert found.email == "repo@test.com"


def test_get_by_email(db_session, regular_user):
    repo = UserRepository(db_session)
    found = repo.get_by_email(regular_user.email)
    assert found is not None
    assert found.id == regular_user.id


def test_get_by_username(db_session, regular_user):
    repo = UserRepository(db_session)
    found = repo.get_by_username(regular_user.username)
    assert found is not None
    assert found.email == regular_user.email


def test_get_by_id_returns_none_for_missing_user(db_session):
    repo = UserRepository(db_session)
    assert repo.get_by_id(uuid.uuid4()) is None


def test_mark_verified(db_session):
    repo = UserRepository(db_session)
    user = User(
        email="verify@test.com",
        username="verifyuser",
        hashed_password=hash_password("secret123"),
        is_verified=False,
        role=UserRole.USER,
    )
    user = repo.create(user)
    updated = repo.mark_verified(user)
    assert updated.is_verified is True


def test_update_password(db_session, regular_user):
    repo = UserRepository(db_session)
    new_hash = hash_password("newpassword123")
    updated = repo.update_password(regular_user, new_hash)
    assert updated.hashed_password == new_hash


def test_update_avatar(db_session, regular_user):
    repo = UserRepository(db_session)
    updated = repo.update_avatar(regular_user, "https://example.com/new.png")
    assert updated.avatar_url == "https://example.com/new.png"
