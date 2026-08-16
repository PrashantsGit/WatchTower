from app.database.session import SessionLocal
from app.models.monitoring_task import MonitoringTask
from app.repositories.monitoring_task_repository import MonitoringTaskRepository


def test_monitoring_task_repository():
    db = SessionLocal()

    try:
        repository = MonitoringTaskRepository(db)

        task = MonitoringTask(
            user_id=41,
            name="Repository Test Task",
            description="Temporary repository test",
            target_url="https://example.com",
            check_interval=60,
            is_active=True,
        )

        created_task = repository.create(task)

        assert created_task.id is not None
        assert created_task.user_id == 41
        assert created_task.name == "Repository Test Task"

        found_task = repository.find_by_id_for_user(
            task_id=created_task.id,
            user_id=41,
        )

        assert found_task is not None
        assert found_task.id == created_task.id

        tasks = repository.list_by_user(user_id=41)

        assert any(
            task.id == created_task.id
            for task in tasks
        )

    finally:
        db.rollback()
        db.close()

def test_monitoring_task_repository_enforces_user_ownership():
    db = SessionLocal()

    try:
        repository = MonitoringTaskRepository(db)

        user_a_task = MonitoringTask(
            user_id=41,
            name="User A Task",
            description="Ownership test",
            target_url="https://example.com/a",
            check_interval=60,
            is_active=True,
        )

        created_task = repository.create(user_a_task)

        own_task = repository.find_by_id_for_user(
            task_id=created_task.id,
            user_id=41,
        )

        assert own_task is not None

        other_user_task = repository.find_by_id_for_user(
            task_id=created_task.id,
            user_id=999999,
        )

        assert other_user_task is None

    finally:
        db.rollback()
        db.close()