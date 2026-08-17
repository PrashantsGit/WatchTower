import pytest
from pydantic import ValidationError

from app.schemas.task import CreateTaskRequest, UpdateTaskRequest


def test_create_task_request_accepts_valid_data():
    request = CreateTaskRequest(
        name="Pixel 8a Price",
        description="Monitor Pixel 8a price",
        target_url="https://example.com/product",
        check_interval=60,
    )

    assert request.name == "Pixel 8a Price"
    assert str(request.target_url) == "https://example.com/product"
    assert request.check_interval == 60


def test_create_task_request_rejects_invalid_url():
    with pytest.raises(ValidationError):
        CreateTaskRequest(
            name="Invalid URL Task",
            description=None,
            target_url="not-a-valid-url",
            check_interval=60,
        )

def test_update_task_request_accepts_valid_data():
    request = UpdateTaskRequest(
        name="Updated Task",
        description="Updated description",
        target_url="https://example.com/updated",
        check_interval=120,
    )

    assert request.name == "Updated Task"
    assert str(request.target_url) == "https://example.com/updated"
    assert request.check_interval == 120

def test_update_task_request_rejects_invalid_url():
    with pytest.raises(ValidationError):
        UpdateTaskRequest(
            name="Invalid URL Task",
            description=None,
            target_url="not-a-valid-url",
            check_interval=60,
        )