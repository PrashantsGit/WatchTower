from uuid import uuid4

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.models.history_event import HistoryEvent
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.models.user import User
from main import app


client = TestClient(app)


def register_and_login(prefix):
    email = f"{prefix}-{uuid4()}@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "History API Test User",
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


def create_task_for_user(
    email,
    name,
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        assert user is not None

        task = MonitoringTask(
            user_id=user.id,
            name=name,
            description="History API integration test",
            target_url="https://example.com",
            check_interval=60,
            is_active=True,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        rule = MonitoringRule(
            task_id=task.id,
            rule_type="KEYWORD",
            operator="contains",
            target_value="Example",
            is_enabled=True,
        )

        snapshot = MonitoringSnapshot(
            task_id=task.id,
            snapshot_data={
                "content": "Example Domain",
            },
            content_hash=f"history-api-{uuid4()}",
            execution_status="SUCCESS",
            response_time_ms=100,
        )

        db.add(rule)
        db.add(snapshot)
        db.commit()

        db.refresh(rule)
        db.refresh(snapshot)

        return task.id, rule.id, snapshot.id

    finally:
        db.close()


def create_history_event(
    task_id,
    rule_id,
    snapshot_id,
    event_type,
):
    db = SessionLocal()

    try:
        event = HistoryEvent(
            task_id=task_id,
            rule_id=rule_id,
            snapshot_id=snapshot_id,
            event_type=event_type,
            previous_value="old",
            current_value="new",
            event_message=f"{event_type} detected.",
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event.id

    finally:
        db.close()


def test_history_api_requires_authentication():
    response = client.get("/api/history")

    assert response.status_code == 401


def test_history_api_lists_only_current_users_history():
    token_a, email_a = register_and_login(
        "history-api-user-a"
    )

    token_b, email_b = register_and_login(
        "history-api-user-b"
    )

    task_a, rule_a, snapshot_a = create_task_for_user(
        email_a,
        "User A History Task",
    )

    task_b, rule_b, snapshot_b = create_task_for_user(
        email_b,
        "User B History Task",
    )

    event_a = create_history_event(
        task_a,
        rule_a,
        snapshot_a,
        "USER_A_EVENT",
    )

    event_b = create_history_event(
        task_b,
        rule_b,
        snapshot_b,
        "USER_B_EVENT",
    )

    response = client.get(
        "/api/history",
        headers={
            "Authorization": f"Bearer {token_a}",
        },
    )

    assert response.status_code == 200

    events = response.json()
    event_ids = [event["id"] for event in events]

    assert event_a in event_ids
    assert event_b not in event_ids


def test_task_history_api_returns_owned_task_history():
    token, email = register_and_login(
        "history-api-task"
    )

    task_id, rule_id, snapshot_id = create_task_for_user(
        email,
        "Task History API Test",
    )

    event_id = create_history_event(
        task_id,
        rule_id,
        snapshot_id,
        "PRICE_DROP",
    )

    response = client.get(
        f"/api/tasks/{task_id}/history",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    events = response.json()

    assert len(events) == 1
    assert events[0]["id"] == event_id
    assert events[0]["task_id"] == task_id
    assert events[0]["rule_id"] == rule_id
    assert events[0]["event_type"] == "PRICE_DROP"
    assert events[0]["previous_value"] == "old"
    assert events[0]["current_value"] == "new"


def test_task_history_api_rejects_other_users_task():
    token_a, email_a = register_and_login(
        "history-api-owner"
    )

    _token_b, email_b = register_and_login(
        "history-api-other"
    )

    task_b, rule_b, snapshot_b = create_task_for_user(
        email_b,
        "Private User B Task",
    )

    create_history_event(
        task_b,
        rule_b,
        snapshot_b,
        "PRIVATE_EVENT",
    )

    response = client.get(
        f"/api/tasks/{task_b}/history",
        headers={
            "Authorization": f"Bearer {token_a}",
        },
    )

    assert response.status_code == 404


def test_task_history_api_returns_404_for_missing_task():
    token, _email = register_and_login(
        "history-api-missing"
    )

    response = client.get(
        "/api/tasks/999999999/history",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404


def test_history_api_supports_pagination():
    token, email = register_and_login(
        "history-api-pagination"
    )

    task_id, rule_id, snapshot_id = create_task_for_user(
        email,
        "History Pagination Task",
    )

    created_event_ids = []

    for index in range(5):
        event_id = create_history_event(
            task_id,
            rule_id,
            snapshot_id,
            f"EVENT_{index}",
        )

        created_event_ids.append(event_id)

    response = client.get(
        "/api/history?limit=2&offset=0",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    first_page = response.json()

    assert len(first_page) == 2

    response = client.get(
        "/api/history?limit=2&offset=2",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    second_page = response.json()

    assert len(second_page) == 2

    first_ids = {
        event["id"]
        for event in first_page
    }

    second_ids = {
        event["id"]
        for event in second_page
    }

    assert first_ids.isdisjoint(second_ids)


def test_history_api_validates_pagination():
    token, _email = register_and_login(
        "history-api-validation"
    )

    response = client.get(
        "/api/history?limit=0",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 422

    response = client.get(
        "/api/history?limit=101",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 422

    response = client.get(
        "/api/history?offset=-1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 422