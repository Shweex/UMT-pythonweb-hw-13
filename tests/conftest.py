"""Shared pytest fixtures for unit and integration tests."""

import os
from collections.abc import Generator
from datetime import date

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure required settings exist before importing application modules.
os.environ.setdefault("AUTH_JWT_SECRET", "test-auth-secret")
os.environ.setdefault("MAIL_JWT_SECRET", "test-mail-secret")
os.environ.setdefault("MAIL_SERVER", "smtp.test.com")
os.environ.setdefault("MAIL_USERNAME", "test@test.com")
os.environ.setdefault("MAIL_PASSWORD", "test-password")
os.environ.setdefault("MAIL_FROM", "test@test.com")
os.environ.setdefault("CLOUDINARY_NAME", "test-cloud")
os.environ.setdefault("CLOUDINARY_API_KEY", "test-key")
os.environ.setdefault("CLOUDINARY_API_SECRET", "test-secret")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ["TEST_DATABASE_URL"] = "sqlite://"

from app.database import Base, get_db
from app.main import app
from app.models import Contact, User, UserRole
from app.services.auth import hash_password
from app.services.cache import UserCache, get_user_cache


@pytest.fixture
def db_engine():
    """Create an in-memory SQLite engine for isolated tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Provide a database session rolled back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def fake_redis():
    """Provide an isolated Redis instance backed by fakeredis."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def user_cache(fake_redis):
    """Return a user cache wired to fakeredis."""
    return UserCache(client=fake_redis)


@pytest.fixture
def client(db_session, user_cache):
    """Return a FastAPI test client with overridden dependencies."""

    def override_get_db():
        yield db_session

    def override_get_user_cache():
        return user_cache

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_cache] = override_get_user_cache
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def regular_user(db_session) -> User:
    """Create a regular user in the test database."""
    user = User(
        email="user@test.com",
        username="testuser",
        hashed_password=hash_password("password123"),
        is_verified=True,
        role=UserRole.USER,
        avatar_url="https://example.com/default.png",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session) -> User:
    """Create an admin user in the test database."""
    user = User(
        email="admin@test.com",
        username="adminuser",
        hashed_password=hash_password("password123"),
        is_verified=True,
        role=UserRole.ADMIN,
        avatar_url="https://example.com/default.png",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, regular_user):
    """Return authorization headers for the regular test user."""
    response = client.post(
        "/api/auth/login",
        json={"username": regular_user.username, "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Return authorization headers for the admin test user."""
    response = client.post(
        "/api/auth/login",
        json={"username": admin_user.username, "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_contact(db_session, regular_user) -> Contact:
    """Create a sample contact owned by the regular user."""
    contact = Contact(
        owner_id=regular_user.id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+380501234567",
        birthday=date(1990, 5, 15),
        additional_data="Friend",
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact
