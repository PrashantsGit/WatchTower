import asyncio
from unittest.mock import patch

from main import app


def test_app_lifespan_starts_and_stops_scheduler():

    async def run_lifespan():
        with patch("main.scheduler_runner") as scheduler_runner_mock:
            async with app.router.lifespan_context(app):
                scheduler_runner_mock.start.assert_called_once_with()

            scheduler_runner_mock.stop.assert_called_once_with()

    asyncio.run(run_lifespan())