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

def test_monitoring_task_repository_updates_task():
    db = SessionLocal()

    task = None

    try:
        repository = MonitoringTaskRepository(db)

        task = MonitoringTask(
            user_id=41,
            name="Original Task",
            description="Original description",
            target_url="https://example.com/original",
            check_interval=60,
            is_active=True,
        )

        task = repository.create(task)

        task.name = "Updated Task"
        task.description = "Updated description"
        task.target_url = "https://example.com/updated"
        task.check_interval = 120

        updated_task = repository.update(task)

        assert updated_task.id == task.id
        assert updated_task.name == "Updated Task"
        assert updated_task.description == "Updated description"
        assert updated_task.target_url == "https://example.com/updated"
        assert updated_task.check_interval == 120

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()

def test_monitoring_task_repository_deletes_task():
    db = SessionLocal()

    task = None

    try:
        repository = MonitoringTaskRepository(db)

        task = MonitoringTask(
            user_id=41,
            name="Delete Test Task",
            description=None,
            target_url="https://example.com",
            check_interval=60,
            is_active=True,
        )

        task = repository.create(task)
        task_id = task.id

        repository.delete(task)

        deleted_task = repository.find_by_id_for_user(
            task_id=task_id,
            user_id=41,
        )

        assert deleted_task is None

    finally:
        db.rollback()
        db.close()

def test_monitoring_task_repository_pauses_task():
    db = SessionLocal()

    task = None

    try:
        repository = MonitoringTaskRepository(db)

        task = MonitoringTask(
            user_id=41,
            name="Pause Test Task",
            description=None,
            target_url="https://example.com",
            check_interval=60,
            is_active=True,
        )

        task = repository.create(task)

        paused_task = repository.pause(task)

        assert paused_task.id == task.id
        assert paused_task.is_active is False

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_monitoring_task_repository_resumes_task():
    db = SessionLocal()

    task = None

    try:
        repository = MonitoringTaskRepository(db)

        task = MonitoringTask(
            user_id=41,
            name="Resume Test Task",
            description=None,
            target_url="https://example.com",
            check_interval=60,
            is_active=False,
        )

        task = repository.create(task)

        resumed_task = repository.resume(task)

        assert resumed_task.id == task.id
        assert resumed_task.is_active is True

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()