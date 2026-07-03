"""Repository for user persistence operations."""

import uuid

from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    """Encapsulates database access for :class:`~app.models.user.User` records."""

    def __init__(self, db: Session) -> None:
        """Initialize the repository with an active database session.

        Args:
            db: SQLAlchemy session bound to the current request or test.
        """
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return a user by primary key or ``None`` if not found."""
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Return a user by email address or ``None`` if not found."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> User | None:
        """Return a user by username or ``None`` if not found."""
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user: User) -> User:
        """Persist a new user and refresh the instance from the database."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Commit pending changes for an existing user."""
        self.db.commit()
        self.db.refresh(user)
        return user

    def mark_verified(self, user: User) -> User:
        """Mark the given user as email-verified."""
        user.is_verified = True
        return self.update(user)

    def update_password(self, user: User, hashed_password: str) -> User:
        """Replace the stored password hash for a user."""
        user.hashed_password = hashed_password
        return self.update(user)

    def update_avatar(self, user: User, avatar_url: str) -> User:
        """Update the avatar URL for a user."""
        user.avatar_url = avatar_url
        return self.update(user)
