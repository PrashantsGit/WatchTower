
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardResponse


class DashboardService:
    """Business logic for the authenticated user's dashboard."""

    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def get_dashboard(self, user_id) -> DashboardResponse:
        since = datetime.now(timezone.utc) - timedelta(hours=24)

        return DashboardResponse(
            total_tasks=self.repository.get_total_tasks(user_id),
            active_tasks=self.repository.get_active_tasks(user_id),
            paused_tasks=self.repository.get_paused_tasks(user_id),
            recent_events=self.repository.get_recent_events(user_id, since),
            pending_notifications=self.repository.get_pending_notifications(
                user_id
            ),
        )
