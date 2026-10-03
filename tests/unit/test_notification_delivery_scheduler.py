from unittest.mock import Mock, patch

from app.scheduler.runner import SchedulerRunner


@patch("app.scheduler.runner.NotificationDeliveryService")
@patch("app.scheduler.runner.SessionLocal")
def test_runner_processes_pending_notifications(
    session_local_mock,
    delivery_service_mock,
):
    db = Mock()
    session_local_mock.return_value = db

    delivery_service = delivery_service_mock.return_value
    runner = SchedulerRunner()

    runner.run_pending_notifications()

    session_local_mock.assert_called_once_with()
    delivery_service_mock.assert_called_once_with(db=db)
    delivery_service.process_pending.assert_called_once_with()
    db.close.assert_called_once_with()


@patch("app.scheduler.runner.NotificationDeliveryService")
@patch("app.scheduler.runner.SessionLocal")
def test_delivery_scheduler_closes_session_after_job_failure(
    session_local_mock,
    delivery_service_mock,
):
    db = Mock()
    session_local_mock.return_value = db

    delivery_service_mock.return_value.process_pending.side_effect = (
        RuntimeError("Unexpected worker error")
    )

    runner = SchedulerRunner()
    runner.run_pending_notifications()

    db.close.assert_called_once_with()