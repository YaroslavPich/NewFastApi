import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app instance is named 'app'
from src.database.database import get_db
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactInDB


@pytest.fixture(scope="module")
def test_app():
    yield app


@pytest.fixture(scope="module")
async def test_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="module")
async def authenticated_user(test_client):
    # Example of authentication token mock
    token = "mock_access_token"
    return token


async def test_create_contact(test_client, authenticated_user):
    # Data for creating a contact
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        "birthday": "1990-01-01"
    }

    # Make POST request to create a contact
    response = await test_client.post("/contacts/", json=contact_data,
                                      headers={"Authorization": f"Bearer {authenticated_user}"})

    # Assert response status code
    assert response.status_code == 200

    # Assert response data matches ContactInDB schema
    created_contact = response.json()
    assert "id" in created_contact
    assert created_contact["first_name"] == contact_data["first_name"]
    assert created_contact["last_name"] == contact_data["last_name"]
    assert created_contact["email"] == contact_data["email"]
    assert created_contact["phone_number"] == contact_data["phone_number"]
    assert created_contact["birthday"] == contact_data["birthday"]

    # Clean up: delete the created contact from the database
    async with get_db() as db:
        await db.execute(Contact.delete().where(Contact.id == created_contact["id"]))
        await db.commit()


async def test_read_contacts(test_client, authenticated_user):
    # Make GET request to retrieve contacts
    response = await test_client.get("/contacts/", headers={"Authorization": f"Bearer {authenticated_user}"})

    # Assert response status code
    assert response.status_code == 200

    # Assert response data is a list of ContactInDB
    contacts = response.json()
    assert isinstance(contacts, list)
    for contact in contacts:
        assert "id" in contact
        assert "first_name" in contact
        assert "last_name" in contact
        assert "email" in contact
        assert "phone_number" in contact
        assert "birthday" in contact

# Additional tests for other routes (read_contact, update_contact, delete_contact) can be added similarly
