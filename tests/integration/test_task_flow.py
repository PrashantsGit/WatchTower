from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def register_and_login():
    email = f"integration-task-{uuid4()}@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Task Integration User",
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

    return response.json()["access_token"]


def test_task_api_flow():
    token = register_and_login()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Create
    response = client.post(
        "/api/tasks",
        headers=headers,
        json={
            "name": "Integration Test Task",
            "description": "Testing task API flow",
            "target_url": "https://example.com",
            "check_interval": 60,
        },
    )

    assert response.status_code == 201

    task = response.json()

    assert task["name"] == "Integration Test Task"
    assert task["target_url"] == "https://example.com/"
    assert task["check_interval"] == 60

    task_id = task["id"]

    # List
    response = client.get(
        "/api/tasks",
        headers=headers,
    )

    assert response.status_code == 200

    tasks = response.json()

    assert any(
        existing_task["id"] == task_id
        for existing_task in tasks
    )

    # Get
    response = client.get(
        f"/api/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id

    # Update
    response = client.put(
        f"/api/tasks/{task_id}",
        headers=headers,
        json={
            "name": "Updated Integration Task",
            "description": "Updated description",
            "target_url": "https://example.com/updated",
            "check_interval": 120,
        },
    )

    assert response.status_code == 200

    updated_task = response.json()

    assert updated_task["name"] == "Updated Integration Task"
    assert updated_task["check_interval"] == 120

    # Pause
    response = client.post(
        f"/api/tasks/{task_id}/pause",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Resume
    response = client.post(
        f"/api/tasks/{task_id}/resume",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    # Delete
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 204

    # Verify deletion
    response = client.get(
        f"/api/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 404