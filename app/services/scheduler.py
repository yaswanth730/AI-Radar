import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import SessionLocal
from app.services.pipeline import execute_scan_cycle

logger = logging.getLogger("ai_radar.scheduler")

scheduler = AsyncIOScheduler()

async def scheduled_scan_job():
    """Async task executed on each scheduler tick."""
    logger.info("Scheduler triggered autonomous AI radar scan cycle...")
    db = SessionLocal()
    try:
        await execute_scan_cycle(db)
    except Exception as e:
        logger.error(f"Error during scheduled scan cycle: {e}")
    finally:
        db.close()

def start_scheduler():
    """Initializes and starts the background scan scheduler."""
    if not scheduler.running:
        scheduler.add_job(
            scheduled_scan_job,
            trigger=IntervalTrigger(minutes=settings.SCAN_INTERVAL_MINUTES),
            id="ai_radar_autonomous_scan",
            name="AI Radar Continuous Primary Source Scan",
            replace_existing=True,
            max_instances=1
        )
        scheduler.start()
        logger.info(f"AI Radar Scheduler started with interval of {settings.SCAN_INTERVAL_MINUTES} minutes.")

def stop_scheduler():
    """Gracefully shuts down the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("AI Radar Scheduler stopped.")
