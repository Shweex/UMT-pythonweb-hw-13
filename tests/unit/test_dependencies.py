"""Unit tests for authentication dependencies."""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies import get_current_user, require_admin
from app.models import User, UserRole
from app.services.auth import create_access_token
from app.services.cache import UserCache


def test_get_current_user_from_cache(db_session, regular_user, fake_redis):
    cache = UserCache(client=fake_redis)
    cache.set_user(
        regular_user.id,
        {
            "id": str(regular_user.id),
            "email": regular_user.email,
            "username": regular_user.username,
            "is_verified": regular_user.is_verified,
            "role": regular_user.role.value,
            "avatar_url": regular_user.avatar_url,
            "created_at": regular_user.created_at.replace(tzinfo=timezone.utc).isoformat(),
        },
    )
    token = create_access_token(str(regular_user.id))
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = get_current_user(credentials=credentials, db=db_session, cache=cache)
    assert user.email == regular_user.email


def test_get_current_user_invalid_token(db_session, fake_redis):
    cache = UserCache(client=fake_redis)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=credentials, db=db_session, cache=cache)
    assert exc.value.status_code == 401


def test_get_current_user_missing_user(db_session, fake_redis):
    cache = UserCache(client=fake_redis)
    token = create_access_token(str(uuid.uuid4()))
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc:
        get_current_user(credentials=credentials, db=db_session, cache=cache)
    assert exc.value.status_code == 401


def test_require_admin_allows_admin(admin_user):
    assert require_admin(current_user=admin_user).role == UserRole.ADMIN


def test_require_admin_rejects_user(regular_user):
    with pytest.raises(HTTPException) as exc:
        require_admin(current_user=regular_user)
    assert exc.value.status_code == 403
