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


def test_rule_api_flow():
    token = register_and_login()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Create task
    response = client.post(
        "/api/tasks",
        headers=headers,
        json={
            "name": "Rule Integration Task",
            "description": "Testing rule API flow",
            "target_url": "https://example.com",
            "check_interval": 60,
        },
    )

    assert response.status_code == 201

    task_id = response.json()["id"]

    # Create rule
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

    assert rule["task_id"] == task_id
    assert rule["rule_type"] == "KEYWORD"
    assert rule["operator"] == "CONTAINS"
    assert rule["target_value"] == "Example Domain"
    assert rule["is_enabled"] is True

    rule_id = rule["id"]

    # List rules
    response = client.get(
        f"/api/tasks/{task_id}/rules",
        headers=headers,
    )

    assert response.status_code == 200

    rules = response.json()

    assert any(
        existing_rule["id"] == rule_id
        for existing_rule in rules
    )

    # Get rule
    response = client.get(
        f"/api/tasks/{task_id}/rules/{rule_id}",
        headers=headers,
    )

    assert response.status_code == 200

    fetched_rule = response.json()

    assert fetched_rule["id"] == rule_id
    assert fetched_rule["task_id"] == task_id
    assert fetched_rule["rule_type"] == "KEYWORD"
    assert fetched_rule["operator"] == "CONTAINS"
    assert fetched_rule["target_value"] == "Example Domain"
    assert fetched_rule["is_enabled"] is True

    # Update rule
    response = client.put(
        f"/api/tasks/{task_id}/rules/{rule_id}",
        headers=headers,
        json={
            "rule_type": "KEYWORD",
            "operator": "contains",
            "target_value": "Updated Example Domain",
            "is_enabled": True,
        },
    )

    assert response.status_code == 200

    updated_rule = response.json()

    assert updated_rule["id"] == rule_id
    assert updated_rule["task_id"] == task_id
    assert updated_rule["rule_type"] == "KEYWORD"
    assert updated_rule["operator"] == "CONTAINS"
    assert updated_rule["target_value"] == "Updated Example Domain"
    assert updated_rule["is_enabled"] is True

    # Delete rule
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

    # Clean up task
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 204