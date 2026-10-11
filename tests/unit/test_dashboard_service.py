
from datetime import timedelta
from unittest.mock import MagicMock, patch

from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardResponse


@patch("app.services.dashboard_service.DashboardRepository")
def test_get_dashboard_returns_all_metrics(repository_class):
    repository = repository_class.return_value
    repository.get_total_tasks.return_value = 10
    repository.get_active_tasks.return_value = 7
    repository.get_paused_tasks.return_value = 3
    repository.get_recent_events.return_value = 5
    repository.get_pending_notifications.return_value = 2

    service = DashboardService(db=MagicMock())

    result = service.get_dashboard(user_id=42)

    assert isinstance(result, DashboardResponse)
    assert result.model_dump() == {
        "total_tasks": 10,
        "active_tasks": 7,
        "paused_tasks": 3,
        "recent_events": 5,
        "pending_notifications": 2,
    }

    repository.get_total_tasks.assert_called_once_with(42)
    repository.get_active_tasks.assert_called_once_with(42)
    repository.get_paused_tasks.assert_called_once_with(42)
    repository.get_recent_events.assert_called_once()
    repository.get_pending_notifications.assert_called_once_with(42)


@patch("app.services.dashboard_service.DashboardRepository")
def test_get_dashboard_returns_zero_metrics(repository_class):
    repository = repository_class.return_value
    repository.get_total_tasks.return_value = 0
    repository.get_active_tasks.return_value = 0
    repository.get_paused_tasks.return_value = 0
    repository.get_recent_events.return_value = 0
    repository.get_pending_notifications.return_value = 0

    service = DashboardService(db=MagicMock())

    result = service.get_dashboard(user_id=42)

    assert result.model_dump() == {
        "total_tasks": 0,
        "active_tasks": 0,
        "paused_tasks": 0,
        "recent_events": 0,
        "pending_notifications": 0,
    }


@patch("app.services.dashboard_service.DashboardRepository")
def test_recent_events_uses_24_hour_window(repository_class):
    repository = repository_class.return_value
    repository.get_total_tasks.return_value = 0
    repository.get_active_tasks.return_value = 0
    repository.get_paused_tasks.return_value = 0
    repository.get_recent_events.return_value = 0
    repository.get_pending_notifications.return_value = 0

    service = DashboardService(db=MagicMock())

    from datetime import datetime, timezone

    before = datetime.now(timezone.utc)
    service.get_dashboard(user_id=42)
    after = datetime.now(timezone.utc)

    since = repository.get_recent_events.call_args.args[1]

    assert before - timedelta(hours=24) <= since
    assert since <= after - timedelta(hours=24)
