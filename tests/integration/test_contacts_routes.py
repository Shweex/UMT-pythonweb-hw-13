"""Integration tests for contact routes."""

from datetime import date, timedelta


def test_create_contact(client, auth_headers):
    response = client.post(
        "/api/contacts",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Roe",
            "email": "jane@example.com",
            "phone": "+380509999999",
            "birthday": "1991-08-20",
            "additional_data": "Colleague",
        },
    )
    assert response.status_code == 201
    assert response.json()["first_name"] == "Jane"


def test_list_contacts(client, auth_headers, sample_contact):
    response = client.get("/api/contacts", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_contact(client, auth_headers, sample_contact):
    response = client.get(f"/api/contacts/{sample_contact.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(sample_contact.id)


def test_get_contact_not_found(client, auth_headers):
    response = client.get(
        "/api/contacts/00000000-0000-0000-0000-000000000001",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_contact(client, auth_headers, sample_contact):
    response = client.put(
        f"/api/contacts/{sample_contact.id}",
        headers=auth_headers,
        json={"first_name": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


def test_delete_contact(client, auth_headers, sample_contact):
    response = client.delete(f"/api/contacts/{sample_contact.id}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/api/contacts/{sample_contact.id}", headers=auth_headers).status_code == 404


def test_search_contacts(client, auth_headers, sample_contact):
    response = client.get("/api/contacts/search", headers=auth_headers, params={"query": "John"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_upcoming_birthdays(client, auth_headers, db_session, regular_user):
    soon = date.today() + timedelta(days=2)
    from app.models import Contact

    contact = Contact(
        owner_id=regular_user.id,
        first_name="Soon",
        last_name="Birthday",
        email="soon@example.com",
        phone="+380504444444",
        birthday=date(2000, soon.month, soon.day),
    )
    db_session.add(contact)
    db_session.commit()

    response = client.get("/api/contacts/upcoming-birthdays", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_contacts_require_authentication(client):
    response = client.get("/api/contacts")
    assert response.status_code == 401
