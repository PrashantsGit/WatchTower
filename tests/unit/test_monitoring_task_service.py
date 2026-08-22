from app.database.session import SessionLocal
from app.services.monitoring_task_service import MonitoringTaskService
import pytest

from app.core.exceptions import ResourceNotFoundError

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

def test_get_task_returns_owned_task():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Get Task Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        found_task = service.get_task(
            task_id=task.id,
            user_id=41,
        )

        assert found_task.id == task.id
        assert found_task.user_id == 41

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_get_task_rejects_other_user():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Ownership Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.get_task(
                task_id=task.id,
                user_id=999999,
            )

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()

def test_update_task_updates_owned_task():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Original Task",
            description="Original description",
            target_url="https://example.com/original",
            check_interval=60,
        )

        original_created_at = task.created_at
        original_user_id = task.user_id

        updated_task = service.update_task(
            task_id=task.id,
            user_id=41,
            name="Updated Task",
            description="Updated description",
            target_url="https://example.com/updated",
            check_interval=120,
        )

        assert updated_task.id == task.id
        assert updated_task.user_id == original_user_id
        assert updated_task.name == "Updated Task"
        assert updated_task.description == "Updated description"
        assert updated_task.target_url == "https://example.com/updated"
        assert updated_task.check_interval == 120
        assert updated_task.created_at == original_created_at

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_update_task_rejects_other_user():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Ownership Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.update_task(
                task_id=task.id,
                user_id=999999,
                name="Should Not Update",
                description=None,
                target_url="https://example.com/changed",
                check_interval=120,
            )

        # Verify the original task was not modified.
        unchanged_task = service.get_task(
            task_id=task.id,
            user_id=41,
        )

        assert unchanged_task.name == "Ownership Test"
        assert unchanged_task.check_interval == 60

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_update_task_rejects_nonexistent_task():
    db = SessionLocal()

    try:
        service = MonitoringTaskService(db)

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.update_task(
                task_id=999999,
                user_id=41,
                name="Should Not Exist",
                description=None,
                target_url="https://example.com",
                check_interval=60,
            )

    finally:
        db.close()

def test_delete_task_deletes_owned_task():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Delete Service Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        task_id = task.id

        service.delete_task(
            task_id=task_id,
            user_id=41,
        )

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.get_task(
                task_id=task_id,
                user_id=41,
            )

        task = None

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_delete_task_rejects_other_user():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Delete Ownership Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.delete_task(
                task_id=task.id,
                user_id=999999,
            )

        # Make sure the task still exists.
        existing_task = service.get_task(
            task_id=task.id,
            user_id=41,
        )

        assert existing_task.id == task.id

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()

def test_pause_task_pauses_owned_task():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Pause Service Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        paused_task = service.pause_task(
            task_id=task.id,
            user_id=41,
        )

        assert paused_task.id == task.id
        assert paused_task.is_active is False

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_resume_task_resumes_owned_task():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Resume Service Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        service.pause_task(
            task_id=task.id,
            user_id=41,
        )

        resumed_task = service.resume_task(
            task_id=task.id,
            user_id=41,
        )

        assert resumed_task.id == task.id
        assert resumed_task.is_active is True

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_pause_task_rejects_other_user():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Pause Ownership Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.pause_task(
                task_id=task.id,
                user_id=999999,
            )

        existing_task = service.get_task(
            task_id=task.id,
            user_id=41,
        )

        assert existing_task.is_active is True

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()


def test_resume_task_rejects_other_user():
    db = SessionLocal()

    task = None

    try:
        service = MonitoringTaskService(db)

        task = service.create_task(
            user_id=41,
            name="Resume Ownership Test",
            description=None,
            target_url="https://example.com",
            check_interval=60,
        )

        service.pause_task(
            task_id=task.id,
            user_id=41,
        )

        with pytest.raises(
            ResourceNotFoundError,
            match="Monitoring task not found",
        ):
            service.resume_task(
                task_id=task.id,
                user_id=999999,
            )

        existing_task = service.get_task(
            task_id=task.id,
            user_id=41,
        )

        assert existing_task.is_active is False

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        db.close()

