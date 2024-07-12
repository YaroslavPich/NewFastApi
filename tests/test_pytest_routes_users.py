from unittest.mock import MagicMock

from src.database.models import Contact


def test_create_contact(client, contact, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.contacts", mock_send_email)
    response = client.post(
        "/contacts/contacts/",
        json=contact,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == contact.get("email")
    assert "id" in data


def test_read_contacts(client):
    response = client.get("/contacts/contacts/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)


def test_read_contact(client, contact):
    response = client.post(
        "/contacts/contacts/",
        json=contact,
    )
    assert response.status_code == 201, response.text
    created_contact = response.json()

    response = client.get(f"/contacts/contacts/{created_contact['id']}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == created_contact['id']


def test_update_contact(client, contact):
    response = client.post(
        "/contacts/contacts/",
        json=contact,
    )
    assert response.status_code == 201, response.text
    created_contact = response.json()

    update_data = {"email": "updated_email@example.com"}

    response = client.put(
        f"/contacts/contacts/{created_contact['id']}",
        json=update_data,
    )
    assert response.status_code == 200, response.text
    updated_contact = response.json()
    assert updated_contact["email"] == update_data["email"]


def test_delete_contact(client, contact):
    response = client.post(
        "/contacts/contacts/",
        json=contact,
    )
    assert response.status_code == 201, response.text
    created_contact = response.json()

    response = client.delete(f"/contacts/contacts/{created_contact['id']}")
    assert response.status_code == 200, response.text
    deleted_contact = response.json()
    assert deleted_contact["id"] == created_contact['id']
