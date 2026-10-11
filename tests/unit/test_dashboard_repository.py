
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.repositories.dashboard_repository import DashboardRepository


def make_repository():
    db = MagicMock()
    repository = DashboardRepository(db)
    return repository, db


def test_get_total_tasks_returns_count():
    repository, db = make_repository()
    db.scalar.return_value = 5

    result = repository.get_total_tasks(user_id=10)

    assert result == 5
    db.scalar.assert_called_once()


def test_get_active_tasks_returns_count():
    repository, db = make_repository()
    db.scalar.return_value = 3

    result = repository.get_active_tasks(user_id=10)

    assert result == 3
    db.scalar.assert_called_once()


def test_get_paused_tasks_returns_count():
    repository, db = make_repository()
    db.scalar.return_value = 2

    result = repository.get_paused_tasks(user_id=10)

    assert result == 2
    db.scalar.assert_called_once()


def test_get_recent_events_returns_count():
    repository, db = make_repository()
    db.scalar.return_value = 4
    since = datetime.now(timezone.utc)

    result = repository.get_recent_events(
        user_id=10,
        since=since,
    )

    assert result == 4
    db.scalar.assert_called_once()


def test_get_pending_notifications_returns_count():
    repository, db = make_repository()
    db.scalar.return_value = 6

    result = repository.get_pending_notifications(user_id=10)

    assert result == 6
    db.scalar.assert_called_once()


def test_dashboard_counts_default_to_zero():
    repository, db = make_repository()
    db.scalar.return_value = None

    assert repository.get_total_tasks(user_id=10) == 0
    assert repository.get_active_tasks(user_id=10) == 0
    assert repository.get_paused_tasks(user_id=10) == 0
    assert repository.get_recent_events(
        user_id=10,
        since=datetime.now(timezone.utc),
    ) == 0
    assert repository.get_pending_notifications(user_id=10) == 0

    assert db.scalar.call_count == 5
