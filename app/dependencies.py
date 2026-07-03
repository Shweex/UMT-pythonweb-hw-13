"""FastAPI dependencies for authentication and authorization."""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.repositories import UserRepository
from app.services.auth import decode_access_token
from app.services.cache import UserCache, get_user_cache

security = HTTPBearer()


def _serialize_user(user: User) -> dict:
    """Convert a SQLAlchemy user into a cache-friendly dictionary."""
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "is_verified": user.is_verified,
        "role": user.role.value,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat(),
    }


def _user_from_cache(data: dict) -> User:
    """Rebuild a detached :class:`User` instance from cached data."""
    from datetime import datetime

    return User(
        id=uuid.UUID(data["id"]),
        email=data["email"],
        username=data["username"],
        is_verified=data["is_verified"],
        role=UserRole(data["role"]),
        avatar_url=data["avatar_url"],
        created_at=datetime.fromisoformat(data["created_at"]),
        hashed_password="",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    cache: UserCache = Depends(get_user_cache),
) -> User:
    """Resolve the authenticated user from cache or the database."""
    user_id_raw = decode_access_token(credentials.credentials)
    if user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = uuid.UUID(user_id_raw)
    cached = cache.get_user(user_id)
    if cached is not None:
        return _user_from_cache(cached)

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    cache.set_user(user.id, _serialize_user(user))
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow access only to users with the admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
