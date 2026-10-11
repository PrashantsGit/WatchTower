
from pydantic import BaseModel, ConfigDict


class DashboardResponse(BaseModel):
    """Aggregated monitoring metrics for the authenticated user."""

    total_tasks: int
    active_tasks: int
    paused_tasks: int
    recent_events: int
    pending_notifications: int

    model_config = ConfigDict(from_attributes=True)

