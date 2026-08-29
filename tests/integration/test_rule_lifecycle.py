from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def register_and_login():
    email = f"integration-rule-{uuid4()}@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Rule Integration User",
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
            "name": "Rule Lifecycle Task",
            "description": "Testing rule lifecycle",
            "target_url": "https://example.com",
            "check_interval": 60,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_rule_lifecycle():
    token = register_and_login()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    task = create_task(headers)
    task_id = task["id"]

    # Create
    response = client.post(
        f"/api/tasks/{task_id}/rules",
        headers=headers,
        json={
            "rule_type": "KEYWORD",
            "operator": "contains",
            "target_value": "Example Domain",
        },
    )

    assert response.status_code == 201

    rule = response.json()
    rule_id = rule["id"]

    assert rule["task_id"] == task_id
    assert rule["rule_type"] == "KEYWORD"
    assert rule["operator"] == "CONTAINS"
    assert rule["target_value"] == "Example Domain"
    assert rule["is_enabled"] is True

    # List
    response = client.get(
        f"/api/tasks/{task_id}/rules",
        headers=headers,
    )

    assert response.status_code == 200

    rules = response.json()

    assert len(rules) == 1
    assert rules[0]["id"] == rule_id

    # Get
    response = client.get(
        f"/api/tasks/{task_id}/rules/{rule_id}",
        headers=headers,
    )

    assert response.status_code == 200

    rule = response.json()

    assert rule["id"] == rule_id
    assert rule["task_id"] == task_id
    assert rule["rule_type"] == "KEYWORD"
    assert rule["operator"] == "CONTAINS"
    assert rule["target_value"] == "Example Domain"
    assert rule["is_enabled"] is True

    # Update
    response = client.put(
        f"/api/tasks/{task_id}/rules/{rule_id}",
        headers=headers,
        json={
            "rule_type": "KEYWORD",
            "operator": "not_contains",
            "target_value": "Something Else",
            "is_enabled": False,
        },
    )

    assert response.status_code == 200

    updated_rule = response.json()

    assert updated_rule["id"] == rule_id
    assert updated_rule["rule_type"] == "KEYWORD"
    assert updated_rule["operator"] == "NOT_CONTAINS"
    assert updated_rule["target_value"] == "Something Else"
    assert updated_rule["is_enabled"] is False

    # Verify update through GET
    response = client.get(
        f"/api/tasks/{task_id}/rules/{rule_id}",
        headers=headers,
    )

    assert response.status_code == 200

    rule = response.json()

    assert rule["operator"] == "NOT_CONTAINS"
    assert rule["target_value"] == "Something Else"
    assert rule["is_enabled"] is False

    # Delete
    response = client.delete(
        f"/api/tasks/{task_id}/rules/{rule_id}",
        headers=headers,
    )

    assert response.status_code == 204

    # Verify deletion
    response = client.get(
        f"/api/tasks/{task_id}/rules/{rule_id}",
        headers=headers,
    )

    assert response.status_code == 404

    # Verify list is empty
    response = client.get(
        f"/api/tasks/{task_id}/rules",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == []