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


def _register_and_login():
    """Register a unique user and return credentials plus an access token."""
    email = f"integration-logout-{uuid4()}@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Logout Integration User",
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200

    return email, password, response.json()["access_token"]


def _login(email: str, password: str) -> str:
    """Log in again and return a separate access token."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_logout_returns_success_response():
    _, _, token = _register_and_login()

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Logged out successfully."
    }


def test_logged_out_token_cannot_access_protected_endpoint():
    _, _, token = _register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = client.post(
        "/api/auth/logout",
        headers=headers,
    )
    assert logout_response.status_code == 200

    response = client.get(
        "/api/auth/me",
        headers=headers,
    )

    assert response.status_code == 401


def test_logout_does_not_invalidate_other_sessions():
    email, password, first_token = _register_and_login()
    second_token = _login(email, password)

    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert logout_response.status_code == 200

    # The logged-out session must be rejected.
    first_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert first_response.status_code == 401

    # The other session for the same user must remain valid.
    second_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert second_response.status_code == 200


def test_repeated_logout_returns_401():
    _, _, token = _register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    first_response = client.post(
        "/api/auth/logout",
        headers=headers,
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/api/auth/logout",
        headers=headers,
    )
    assert second_response.status_code == 401
