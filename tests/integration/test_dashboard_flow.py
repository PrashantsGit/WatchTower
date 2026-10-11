
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.models.history_event import HistoryEvent
from app.models.monitoring_rule import MonitoringRule
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.monitoring_task import MonitoringTask
from app.models.notification import Notification
from app.models.user import User
from main import app


client = TestClient(app)


def register_and_login(prefix):
    email = f"{prefix}-{uuid4()}@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Dashboard API Test User",
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


def create_task(email, name, is_active=True):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None

        task = MonitoringTask(
            user_id=user.id,
            name=name,
            target_url="https://example.com",
            check_interval=60,
            is_active=is_active,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        return task.id
    finally:
        db.close()


def create_event(task_id, detected_at=None, with_pending_notification=False):
    db = SessionLocal()

    try:
        task = db.get(MonitoringTask, task_id)
        assert task is not None

        rule = MonitoringRule(
            task_id=task_id,
            rule_type="KEYWORD",
            operator="contains",
            target_value="Example",
            is_enabled=True,
        )

        snapshot = MonitoringSnapshot(
            task_id=task_id,
            snapshot_data={"content": "Example Domain"},
            content_hash=f"dashboard-{uuid4().hex}",
            execution_status="SUCCESS",
            response_time_ms=100,
        )

        db.add_all([rule, snapshot])
        db.commit()
        db.refresh(rule)
        db.refresh(snapshot)

        event = HistoryEvent(
            task_id=task_id,
            rule_id=rule.id,
            snapshot_id=snapshot.id,
            event_type="TEST_EVENT",
            previous_value="old",
            current_value="new",
            event_message="Dashboard integration test event",
        )
        if detected_at is not None:
            event.detected_at = detected_at

        db.add(event)
        db.commit()
        db.refresh(event)

        if with_pending_notification:
            notification = Notification(
                history_event_id=event.id,
                notification_channel="EMAIL",
                notification_status="PENDING",
            )
            db.add(notification)
            db.commit()

        return event.id
    finally:
        db.close()


def test_dashboard_requires_authentication():
    response = client.get("/api/dashboard")

    assert response.status_code == 401


def test_dashboard_returns_documented_response_fields():
    token, _email = register_and_login("dashboard-fields")

    response = client.get(
        "/api/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert set(response.json()) == {
        "total_tasks",
        "active_tasks",
        "paused_tasks",
        "recent_events",
        "pending_notifications",
    }


def test_dashboard_returns_zero_for_empty_account():
    token, _email = register_and_login("dashboard-empty")

    response = client.get(
        "/api/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 0,
        "active_tasks": 0,
        "paused_tasks": 0,
        "recent_events": 0,
        "pending_notifications": 0,
    }


def test_dashboard_counts_only_current_users_data():
    token_a, email_a = register_and_login("dashboard-owner")
    _token_b, email_b = register_and_login("dashboard-other")

    active_task_id = create_task(
        email_a,
        "Owner Active Task",
        is_active=True,
    )
    create_task(
        email_a,
        "Owner Paused Task",
        is_active=False,
    )

    other_task_id = create_task(
        email_b,
        "Other User Task",
        is_active=True,
    )

    now = datetime.now(timezone.utc)

    create_event(
        active_task_id,
        detected_at=now - timedelta(hours=1),
        with_pending_notification=True,
    )
    create_event(
        other_task_id,
        detected_at=now - timedelta(hours=1),
        with_pending_notification=True,
    )

    response = client.get(
        "/api/dashboard",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_tasks": 2,
        "active_tasks": 1,
        "paused_tasks": 1,
        "recent_events": 1,
        "pending_notifications": 1,
    }


def test_dashboard_recent_events_use_24_hour_window():
    token, email = register_and_login("dashboard-window")
    task_id = create_task(email, "Dashboard Window Task")

    now = datetime.now(timezone.utc)

    create_event(
        task_id,
        detected_at=now - timedelta(hours=2),
    )
    create_event(
        task_id,
        detected_at=now - timedelta(hours=26),
    )

    response = client.get(
        "/api/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["recent_events"] == 1
