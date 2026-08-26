from apscheduler.schedulers.background import BackgroundScheduler

from app.database.session import SessionLocal
from app.scheduler.service import SchedulerService


class SchedulerRunner:

    def __init__(self, engine):
        self.engine = engine
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        self.scheduler.add_job(
            self.run_pending,
            "interval",
            minutes=1,
            id="monitoring_scheduler",
            replace_existing=True,
        )

        self.scheduler.start()

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()

    def run_pending(self) -> None:
        db = SessionLocal()

        try:
            scheduler_service = SchedulerService(
                db=db,
                engine=self.engine,
            )

            scheduler_service.run_pending()

        finally:
            db.close()