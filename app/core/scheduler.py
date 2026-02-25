"""
Background scheduler: process PENDING scheduled jobs whose run_at <= now.
"""
import threading
import time
from datetime import datetime

from app.config import settings
from app.db import SessionLocal
from app.core.engine import execute_node
from app.models import ScheduledJob
from app.models.scheduled_job import JobStatus


def _run_scheduler_once():
    """Process one batch of due jobs."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        jobs = (
            db.query(ScheduledJob)
            .filter(
                ScheduledJob.status == JobStatus.PENDING.value,
                ScheduledJob.run_at <= now,
            )
            .limit(50)
            .all()
        )
        for job in jobs:
            try:
                job.status = JobStatus.RUNNING.value
                db.commit()
                job_db = SessionLocal()
                try:
                    execute_node(job_db, job.participant_id, job.node_id)
                finally:
                    job_db.close()
                job.status = JobStatus.DONE.value
                db.commit()
            except Exception:
                db.rollback()
                job.status = JobStatus.PENDING.value
                db.commit()
    finally:
        db.close()


_running = False
_thread = None


def start_scheduler():
    """Start background thread that polls scheduled jobs."""
    global _running, _thread
    if _running:
        return
    _running = True
    interval = max(1, getattr(settings, "SCHEDULER_POLL_INTERVAL_SECONDS", 1))

    def loop():
        while _running:
            try:
                _run_scheduler_once()
            except Exception:
                pass
            time.sleep(interval)

    _thread = threading.Thread(target=loop, daemon=True)
    _thread.start()


def stop_scheduler():
    """Stop the background scheduler."""
    global _running
    _running = False
