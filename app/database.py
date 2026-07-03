"""Database engine and session configuration."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""


@lru_cache
def get_engine():
    """Create and cache the SQLAlchemy engine."""
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory():
    """Create and cache the SQLAlchemy session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    """Yield a database session and ensure it is closed afterward."""
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
