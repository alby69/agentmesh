import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from podcast_generator.config import Settings
from podcast_generator.pipeline import daily_episode, weekly_episode

logger = logging.getLogger(__name__)

class MeshScheduler:
    """Manages automated tasks for the podcast generator."""

    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()

    def _setup_jobs(self):
        # Daily episode at 8:00 AM
        self.scheduler.add_job(
            self.run_daily,
            CronTrigger(hour=8, minute=0),
            id="daily_podcast",
            replace_existing=True
        )

        # Weekly episode on Monday at 9:00 AM
        self.scheduler.add_job(
            self.run_weekly,
            CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="weekly_podcast",
            replace_existing=True
        )

        logger.info("Scheduler configured: Daily (8:00), Weekly (Mon 9:00)")

    async def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("MeshScheduler started.")

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("MeshScheduler stopped.")

    async def run_daily(self):
        logger.info("Auto-executing daily podcast task...")
        try:
            path = await daily_episode(self.cfg)
            logger.info(f"Auto daily complete: {path}")
        except Exception as e:
            logger.error(f"Auto daily failed: {e}")

    async def run_weekly(self):
        logger.info("Auto-executing weekly podcast task...")
        try:
            path = await weekly_episode(self.cfg, days=7)
            logger.info(f"Auto weekly complete: {path}")
        except Exception as e:
            logger.error(f"Auto weekly failed: {e}")
