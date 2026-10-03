from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationTaskSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_url: str


class NotificationHistoryEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    event_type: str
    previous_value: str | None
    current_value: str | None
    event_message: str | None
    detected_at: datetime
    task: NotificationTaskSummaryResponse


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    history_event_id: int
    notification_channel: str
    notification_status: str
    delivered_at: datetime | None
    error_message: str | None
    created_at: datetime
    history_event: NotificationHistoryEventResponse