from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CreateTaskRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    target_url: HttpUrl
    check_interval: int = 60

class UpdateTaskRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    target_url: HttpUrl
    check_interval: int


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    target_url: str
    check_interval: int
    is_active: bool
    last_checked_at: datetime | None
    next_execution_at: datetime | None
    created_at: datetime
    updated_at: datetime