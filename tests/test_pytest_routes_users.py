import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import status
from src.routes import auth


@pytest.fixture
def client():
    return TestClient(auth.router)


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/user/users/signup",  # Fixed URL here
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_login_user_not_confirmed(client, user):
    response = client.post("/user/users/login", data={"username": user["email"], "password": user["password"]})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_send_test_email(client):
    response = client.post("/user/users/send_test_email", json={"email_to_send": "test@example.com"})

    assert response.status_code == status.HTTP_200_OK


