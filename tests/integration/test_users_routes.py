"""Integration tests for user profile routes."""

from unittest.mock import patch


def test_get_current_user_profile(client, auth_headers, regular_user):
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == regular_user.email
    assert data["role"] == "user"


def test_get_current_user_unauthorized(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401


@patch("app.routers.users.upload_avatar", return_value="https://example.com/avatar.png")
def test_admin_can_update_avatar(mock_upload, client, admin_auth_headers):
    response = client.patch(
        "/api/users/me/avatar",
        headers=admin_auth_headers,
        files={"file": ("avatar.png", b"fake-image", "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["avatar_url"] == "https://example.com/avatar.png"
    mock_upload.assert_called_once()


def test_regular_user_cannot_update_avatar(client, auth_headers):
    response = client.patch(
        "/api/users/me/avatar",
        headers=auth_headers,
        files={"file": ("avatar.png", b"fake-image", "image/png")},
    )
    assert response.status_code == 403


def test_update_avatar_requires_image(client, admin_auth_headers):
    response = client.patch(
        "/api/users/me/avatar",
        headers=admin_auth_headers,
        files={"file": ("doc.txt", b"text", "text/plain")},
    )
    assert response.status_code == 400


def test_get_current_user_uses_cache(client, auth_headers, regular_user, user_cache, db_session):
    client.get("/api/users/me", headers=auth_headers)
    assert user_cache.get_user(regular_user.id) is not None

    db_session.delete(regular_user)
    db_session.commit()

    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == regular_user.email
