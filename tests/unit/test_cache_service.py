"""Unit tests for Redis user cache helpers."""

import uuid

from app.services.cache import UserCache


def test_set_get_and_delete_user(fake_redis):
    cache = UserCache(client=fake_redis)
    user_id = uuid.uuid4()
    payload = {
        "id": str(user_id),
        "email": "cache@test.com",
        "username": "cacheuser",
        "is_verified": True,
        "role": "user",
        "avatar_url": None,
        "created_at": "2026-01-01T00:00:00+00:00",
    }

    assert cache.get_user(user_id) is None
    cache.set_user(user_id, payload)
    assert cache.get_user(user_id) == payload
    cache.delete_user(user_id)
    assert cache.get_user(user_id) is None
