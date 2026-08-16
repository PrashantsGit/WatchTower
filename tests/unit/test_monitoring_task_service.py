from app.database.session import SessionLocal
from app.services.monitoring_task_service import MonitoringTaskService


def test_create_task():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="  Test Monitoring Task  ",
            description="  Test description  ",
            target_url="  https://example.com  ",
            check_interval=60,
        )

        assert task.id is not None
        assert task.user_id == 41
        assert task.name == "Test Monitoring Task"
        assert task.description == "Test description"
        assert task.target_url == "https://example.com"
        assert task.check_interval == 60
        assert task.is_active is True

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_list_tasks_returns_only_user_tasks():
    db = SessionLocal()

    task_1 = None
    task_2 = None

    try:
        service = MonitoringTaskService(db)

        task_1 = service.create_task(
            user_id=41,
            name="User 41 Task",
            description=None,
            target_url="https://example.com/1",
            check_interval=60,
        )

        task_2 = service.create_task(
            user_id=41,
            name="User 41 Task 2",
            description=None,
            target_url="https://example.com/2",
            check_interval=120,
        )

        tasks = service.list_tasks(user_id=41)

        task_ids = {task.id for task in tasks}

        assert task_1.id in task_ids
        assert task_2.id in task_ids

    finally:
        if task_1 is not None:
            db.delete(task_1)

        if task_2 is not None:
            db.delete(task_2)

        db.commit()
        db.close()