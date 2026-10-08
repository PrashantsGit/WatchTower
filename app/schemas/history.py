from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    rule_id: int
    event_type: str
    previous_value: str | None
    current_value: str | None
    event_message: str | None
    detected_at: datetime