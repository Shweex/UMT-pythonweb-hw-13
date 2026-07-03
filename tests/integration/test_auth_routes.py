"""Integration tests for authentication routes."""

from unittest.mock import AsyncMock, patch

from app.services.auth import create_email_verification_token, create_password_reset_token


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Contacts REST API is running"


@patch("app.routers.auth.send_verification_email", new_callable=AsyncMock)
def test_register_user(mock_send_email, client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new@test.com", "username": "newuser", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["role"] == "user"
    mock_send_email.assert_awaited_once()


def test_register_duplicate_email(client, regular_user):
    response = client.post(
        "/api/auth/register",
        json={"email": regular_user.email, "username": "another", "password": "password123"},
    )
    assert response.status_code == 409


def test_login_success(client, regular_user, user_cache):
    response = client.post(
        "/api/auth/login",
        json={"username": regular_user.username, "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    cached = user_cache.get_user(regular_user.id)
    assert cached is not None
    assert cached["email"] == regular_user.email


def test_login_invalid_credentials(client, regular_user):
    response = client.post(
        "/api/auth/login",
        json={"username": regular_user.username, "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_verify_email(client, db_session, regular_user):
    regular_user.is_verified = False
    db_session.commit()
    token = create_email_verification_token(regular_user.email)
    response = client.get(f"/api/auth/verify/{token}")
    assert response.status_code == 200
    assert response.json()["email"] == regular_user.email


def test_verify_email_invalid_token(client):
    response = client.get("/api/auth/verify/invalid-token")
    assert response.status_code == 400


@patch("app.routers.auth.send_password_reset_email", new_callable=AsyncMock)
def test_forgot_password(mock_send_email, client, regular_user):
    response = client.post("/api/auth/forgot-password", json={"email": regular_user.email})
    assert response.status_code == 200
    mock_send_email.assert_awaited_once()


@patch("app.routers.auth.send_password_reset_email", new_callable=AsyncMock)
def test_forgot_password_unknown_email(mock_send_email, client):
    response = client.post("/api/auth/forgot-password", json={"email": "missing@test.com"})
    assert response.status_code == 200
    mock_send_email.assert_not_awaited()


def test_reset_password(client, regular_user, user_cache):
    user_cache.set_user(regular_user.id, {"id": str(regular_user.id)})
    token = create_password_reset_token(regular_user.email)
    response = client.post(
        f"/api/auth/reset-password/{token}",
        json={"new_password": "newpassword123"},
    )
    assert response.status_code == 200
    assert user_cache.get_user(regular_user.id) is None

    login_response = client.post(
        "/api/auth/login",
        json={"username": regular_user.username, "password": "newpassword123"},
    )
    assert login_response.status_code == 200


def test_reset_password_invalid_token(client):
    response = client.post(
        "/api/auth/reset-password/bad-token",
        json={"new_password": "newpassword123"},
    )
    assert response.status_code == 400
