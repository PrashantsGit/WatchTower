from unittest.mock import Mock, patch

from app.scheduler.runner import SchedulerRunner


def test_runner_starts_scheduler():
    engine = Mock()
    runner = SchedulerRunner(engine=engine)

    with patch.object(runner.scheduler, "start") as start_mock:
        runner.start()

        start_mock.assert_called_once()

    assert runner.scheduler.get_job("monitoring_scheduler") is not None

    runner.scheduler.remove_all_jobs()


def test_runner_stops_scheduler():
    engine = Mock()
    runner = SchedulerRunner(engine=engine)

    runner.scheduler = Mock()
    runner.scheduler.running = True

    runner.stop()

    runner.scheduler.shutdown.assert_called_once_with()
    
@patch("app.scheduler.runner.SchedulerService")
@patch("app.scheduler.runner.SessionLocal")
def test_runner_creates_scheduler_service_and_runs_pending(
    session_local_mock,
    scheduler_service_mock,
):
    engine = Mock()
    db = Mock()

    session_local_mock.return_value = db

    scheduler_service = scheduler_service_mock.return_value

    runner = SchedulerRunner(engine=engine)

    runner.run_pending()

    session_local_mock.assert_called_once_with()

    scheduler_service_mock.assert_called_once_with(
        db=db,
        engine=engine,
    )

    scheduler_service.run_pending.assert_called_once_with()

    db.close.assert_called_once_with()