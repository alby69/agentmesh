import logging
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("newsletter_filter.scheduler")


class MeshScheduler:
    """Periodic automatic scanning of RSS/IMAP sources via APScheduler."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()

    def _setup_jobs(self):
        self.scheduler.add_job(
            self.run_rss_scan,
            CronTrigger(hour=8, minute=0),
            id="daily_rss_scan",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.run_imap_scan,
            CronTrigger(hour=9, minute=0),
            id="daily_imap_scan",
            replace_existing=True,
        )
        logger.info("Scheduler configured: RSS (8:00), IMAP (9:00)")

    async def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("MeshScheduler started.")

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("MeshScheduler stopped.")

    async def run_rss_scan(self):
        from newsletter_filter.web.app import _run_scanning_background

        logger.info("Auto-executing RSS scan...")
        job_id = str(uuid.uuid4())
        try:
            await _run_scanning_background(job_id, "rss")
            logger.info(f"Auto RSS scan completed (job {job_id}).")
        except Exception as e:
            logger.error(f"Auto RSS scan failed: {e}")

    async def run_imap_scan(self):
        from newsletter_filter.web.app import load_effective_settings, _run_scanning_background

        settings = load_effective_settings()
        if not settings.imap_host or not settings.imap_user:
            logger.info("IMAP not configured, skipping auto IMAP scan.")
            return

        logger.info("Auto-executing IMAP scan...")
        job_id = str(uuid.uuid4())
        try:
            await _run_scanning_background(job_id, "imap")
            logger.info(f"Auto IMAP scan completed (job {job_id}).")
        except Exception as e:
            logger.error(f"Auto IMAP scan failed: {e}")
