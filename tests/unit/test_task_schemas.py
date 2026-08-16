import pytest
from pydantic import ValidationError

from app.schemas.task import CreateTaskRequest


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