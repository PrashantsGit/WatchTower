from uuid import uuid4

from fastapi.testclient import TestClient

from main import app
from app.database.session import SessionLocal
from app.models.history_event import HistoryEvent
from app.models.monitoring_snapshot import MonitoringSnapshot
from app.models.user import User
from app.monitoring.engine import MonitoringEngineService


client = TestClient(app)


def register_and_login():
    email = f"integration-monitoring-{uuid4()}@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Monitoring Integration User",
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


def test_monitoring_execution_with_real_website():
    token, email = register_and_login()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    # Create monitoring task
    response = client.post(
        "/api/tasks",
        headers=headers,
        json={
            "name": "Real Website Monitoring Test",
            "description": "Testing monitoring execution against example.com",
            "target_url": "https://example.com",
            "check_interval": 60,
        },
    )

    assert response.status_code == 201

    task = response.json()
    task_id = task["id"]

    # Create keyword rule
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

    db = SessionLocal()

    try:
        # Get authenticated user's ID
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        assert user is not None

        user_id = user.id

        # Execute monitoring engine against real website
        engine = MonitoringEngineService(db=db)

        context = engine.execute(
            task_id=task_id,
            user_id=user_id,
        )

        assert context is not None

        # Verify real retrieval
        assert context.page.status_code == 200
        assert context.page.url.startswith(
            "https://example.com"
        )

        # Verify extraction
        assert context.data.text is not None
        assert "Example Domain" in context.data.text

        # Verify rule evaluation
        assert len(context.evaluations) == 1

        evaluation = context.evaluations[0]

        assert evaluation.rule.id == rule_id
        assert evaluation.matched is True

        # Verify snapshot was persisted
        snapshot = (
            db.query(MonitoringSnapshot)
            .filter(
                MonitoringSnapshot.task_id == task_id,
                MonitoringSnapshot.execution_status == "SUCCESS",
            )
            .order_by(MonitoringSnapshot.id.desc())
            .first()
        )

        assert snapshot is not None
        assert snapshot.snapshot_data["text"] is not None
        assert "Example Domain" in snapshot.snapshot_data["text"]
        assert len(snapshot.content_hash) == 64

        # Verify history event was persisted
        history_event = (
            db.query(HistoryEvent)
            .filter(
                HistoryEvent.task_id == task_id,
                HistoryEvent.rule_id == rule_id,
                HistoryEvent.snapshot_id == snapshot.id,
            )
            .order_by(HistoryEvent.id.desc())
            .first()
        )

        assert history_event is not None
        assert history_event.event_type == "KEYWORD_DETECTED"
        assert history_event.event_message == (
            "Keyword condition triggered."
        )

    finally:
        db.close()

    # Clean up task
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 204