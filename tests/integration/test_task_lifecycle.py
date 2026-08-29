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


def create_task(headers):
    response = client.post(
        "/api/tasks",
        headers=headers,
        json={
            "name": "Task Lifecycle Test",
            "description": "Testing task lifecycle",
            "target_url": "https://example.com",
            "check_interval": 60,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_task_lifecycle():
    token = register_and_login()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Create
    task = create_task(headers)

    task_id = task["id"]

    assert task["name"] == "Task Lifecycle Test"
    assert task["is_active"] is True

    # Get
    response = client.get(
        f"/api/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 200

    task = response.json()

    assert task["id"] == task_id
    assert task["is_active"] is True

    # List
    response = client.get(
        "/api/tasks",
        headers=headers,
    )

    assert response.status_code == 200

    tasks = response.json()

    assert any(
        task["id"] == task_id
        for task in tasks
    )

    # Pause
    response = client.post(
        f"/api/tasks/{task_id}/pause",
        headers=headers,
    )

    assert response.status_code == 200

    paused_task = response.json()

    assert paused_task["is_active"] is False
    assert paused_task["message"] == (
        "Monitoring task paused."
    )

    # Get after pause
    response = client.get(
        f"/api/tasks/{task_id}",
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

    resumed_task = response.json()

    assert resumed_task["is_active"] is True
    assert resumed_task["message"] == (
        "Monitoring task resumed."
    )

    # Get after resume
    response = client.get(
        f"/api/tasks/{task_id}",
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