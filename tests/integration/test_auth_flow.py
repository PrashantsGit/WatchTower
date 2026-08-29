from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_auth_flow():
    email = f"integration-auth-{uuid4()}@example.com"
    password = "testpassword123"

    # Register
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Integration Test User",
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    registration = response.json()

    assert registration["message"] == (
        "User registered successfully."
    )

    user = registration["user"]

    assert user["email"] == email
    assert user["full_name"] == "Integration Test User"
    assert user["id"] is not None

    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    login_response = response.json()

    assert login_response["access_token"]
    assert login_response["token_type"] == "bearer"

    token = login_response["access_token"]

    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    current_user = response.json()

    assert current_user["id"] == user["id"]
    assert current_user["email"] == email
    assert current_user["full_name"] == "Integration Test User"