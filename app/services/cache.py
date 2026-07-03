"""Redis-backed caching helpers for user data."""

import json
import uuid
from typing import Any

import redis

from app.config import get_settings

settings = get_settings()


class UserCache:
    """Store and retrieve serialized user payloads in Redis."""

    def __init__(self, client: redis.Redis | None = None) -> None:
        """Create a cache helper using the provided Redis client or a default one."""
        self.client = client or redis.Redis.from_url(settings.redis_url, decode_responses=True)

    @staticmethod
    def _key(user_id: uuid.UUID) -> str:
        """Build the Redis key for a cached user."""
        return f"user:{user_id}"

    def get_user(self, user_id: uuid.UUID) -> dict[str, Any] | None:
        """Return cached user data or ``None`` when the key is missing."""
        raw = self.client.get(self._key(user_id))
        if raw is None:
            return None
        return json.loads(raw)

    def set_user(self, user_id: uuid.UUID, data: dict[str, Any]) -> None:
        """Cache user data with a configurable TTL."""
        self.client.setex(
            self._key(user_id),
            settings.redis_user_cache_ttl_seconds,
            json.dumps(data),
        )

    def delete_user(self, user_id: uuid.UUID) -> None:
        """Remove cached user data to keep profile information fresh."""
        self.client.delete(self._key(user_id))


def get_user_cache() -> UserCache:
    """Return a shared cache instance for dependency injection."""
    return UserCache()
