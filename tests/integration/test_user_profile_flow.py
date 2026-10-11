
from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def register_and_login(prefix: str, full_name: str = "Profile Test User"):
    email = f"{prefix}-{uuid4()}@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": full_name,
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

    return response.json()["access_token"], email


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_get_my_profile_requires_authentication():
    response = client.get("/api/users/me")

    assert response.status_code == 401


def test_get_my_profile_returns_public_fields():
    token, email = register_and_login(
        "profile-get",
        full_name="Profile Test User",
    )

    response = client.get(
        "/api/users/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Profile Test User"
    assert response.json()["email"] == email
    assert isinstance(response.json()["id"], int)
    assert set(response.json()) == {"id", "full_name", "email"}


def test_update_my_profile_changes_full_name():
    token, email = register_and_login("profile-update")

    response = client.put(
        "/api/users/me",
        headers=auth_headers(token),
        json={"full_name": "Updated Profile Name"},
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Profile Name"
    assert response.json()["email"] == email
    assert set(response.json()) == {"id", "full_name", "email"}

    profile_response = client.get(
        "/api/users/me",
        headers=auth_headers(token),
    )

    assert profile_response.status_code == 200
    assert profile_response.json()["full_name"] == "Updated Profile Name"


def test_update_my_profile_requires_authentication():
    response = client.put(
        "/api/users/me",
        json={"full_name": "Updated Name"},
    )

    assert response.status_code == 401


def test_update_my_profile_rejects_whitespace_name():
    token, _email = register_and_login("profile-blank")

    response = client.put(
        "/api/users/me",
        headers=auth_headers(token),
        json={"full_name": "   "},
    )

    assert response.status_code == 422


def test_profile_update_does_not_change_another_users_profile():
    token_a, email_a = register_and_login(
        "profile-owner-a",
        full_name="Owner A",
    )
    token_b, email_b = register_and_login(
        "profile-owner-b",
        full_name="Owner B",
    )

    response = client.put(
        "/api/users/me",
        headers=auth_headers(token_a),
        json={"full_name": "Updated Owner A"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == email_a

    other_profile = client.get(
        "/api/users/me",
        headers=auth_headers(token_b),
    )

    assert other_profile.status_code == 200
    assert other_profile.json()["email"] == email_b
    assert other_profile.json()["full_name"] == "Owner B"


def test_auth_me_remains_backward_compatible():
    token, email = register_and_login(
        "profile-auth-me",
        full_name="Existing Auth Profile",
    )

    response = client.get(
        "/api/auth/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["full_name"] == "Existing Auth Profile"
    assert "is_verified" in response.json()
    assert "is_active" in response.json()
