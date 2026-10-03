import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.database.session import SessionLocal
from app.monitoring.engine import MonitoringEngineService
from app.scheduler.service import SchedulerService
from app.services.notification_delivery_service import (
    NotificationDeliveryService,
)


logger = logging.getLogger(__name__)


class SchedulerRunner:

    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        self.scheduler.add_job(
            self.run_pending,
            "interval",
            minutes=1,
            id="monitoring_scheduler",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        self.scheduler.add_job(
            self.run_pending_notifications,
            "interval",
            minutes=1,
            id="notification_delivery_scheduler",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

        self.scheduler.start()

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()

    def run_pending(self) -> None:
        db = SessionLocal()

        try:
            engine = MonitoringEngineService(db=db)
            scheduler_service = SchedulerService(
                db=db,
                engine=engine,
            )
            scheduler_service.run_pending()
        finally:
            db.close()

    def run_pending_notifications(self) -> None:
        db = SessionLocal()

        try:
            delivery_service = NotificationDeliveryService(
                db=db,
            )
            delivery_service.process_pending()
        except Exception:
            logger.exception(
                "Notification delivery job failed."
            )
        finally:
            db.close()