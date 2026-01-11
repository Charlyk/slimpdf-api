"""File cleanup task for removing expired files and jobs."""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session_maker
from app.models import Job, JobStatus
from app.services.file_manager import file_manager

settings = get_settings()


async def cleanup_expired_jobs(db: AsyncSession) -> int:
    """
    Clean up expired jobs and their files.

    Returns:
        Number of jobs cleaned up
    """
    now = datetime.utcnow()
    cleaned = 0

    # Find expired jobs with files
    result = await db.execute(
        select(Job).where(
            Job.expires_at < now,
            Job.file_path.isnot(None),
        )
    )
    expired_jobs = result.scalars().all()

    for job in expired_jobs:
        # Delete the file
        if job.file_path:
            file_path = Path(job.file_path)
            if file_path.exists():
                try:
                    file_path.unlink()
                    cleaned += 1
                except OSError:
                    pass

        # Clear file path
        job.file_path = None

    await db.commit()
    return cleaned


async def cleanup_old_jobs(db: AsyncSession, days: int = 7) -> int:
    """
    Delete job records older than specified days.

    Args:
        db: Database session
        days: Number of days after which to delete jobs

    Returns:
        Number of jobs deleted
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        delete(Job).where(
            Job.created_at < cutoff,
            Job.file_path.is_(None),  # Only delete jobs without files
        )
    )
    await db.commit()
    return result.rowcount


async def cleanup_orphaned_files() -> int:
    """
    Clean up files in temp directories that are older than 24 hours.

    This catches any files that weren't properly cleaned up.

    Returns:
        Number of files deleted
    """
    return file_manager.cleanup_expired_files(max_age_hours=24)


async def cleanup_failed_jobs(db: AsyncSession, hours: int = 24) -> int:
    """
    Clean up files from failed jobs older than specified hours.

    Args:
        db: Database session
        hours: Hours after which to clean up failed job files

    Returns:
        Number of jobs cleaned
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    cleaned = 0

    result = await db.execute(
        select(Job).where(
            Job.status == JobStatus.FAILED,
            Job.created_at < cutoff,
            Job.file_path.isnot(None),
        )
    )
    failed_jobs = result.scalars().all()

    for job in failed_jobs:
        if job.file_path:
            file_path = Path(job.file_path)
            if file_path.exists():
                try:
                    file_path.unlink()
                    cleaned += 1
                except OSError:
                    pass
            job.file_path = None

    await db.commit()
    return cleaned


async def run_cleanup() -> dict:
    """
    Run all cleanup tasks.

    Returns:
        Dictionary with cleanup statistics
    """
    stats = {
        "expired_jobs_cleaned": 0,
        "old_jobs_deleted": 0,
        "orphaned_files_deleted": 0,
        "failed_jobs_cleaned": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }

    async with async_session_maker() as db:
        # Clean expired job files
        stats["expired_jobs_cleaned"] = await cleanup_expired_jobs(db)

        # Clean failed job files
        stats["failed_jobs_cleaned"] = await cleanup_failed_jobs(db)

        # Delete old job records
        stats["old_jobs_deleted"] = await cleanup_old_jobs(db)

    # Clean orphaned files (runs outside db session)
    stats["orphaned_files_deleted"] = await asyncio.to_thread(
        cleanup_orphaned_files
    )

    return stats


async def cleanup_loop(interval_minutes: int = 15):
    """
    Run cleanup in a loop.

    Args:
        interval_minutes: Minutes between cleanup runs
    """
    while True:
        try:
            stats = await run_cleanup()
            total = sum(v for k, v in stats.items() if isinstance(v, int))
            if total > 0:
                print(f"Cleanup completed: {stats}")
        except Exception as e:
            print(f"Cleanup error: {e}")

        await asyncio.sleep(interval_minutes * 60)


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run file cleanup tasks")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run cleanup in a loop",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Interval in minutes for loop mode",
    )
    args = parser.parse_args()

    if args.loop:
        print(f"Starting cleanup loop (every {args.interval} minutes)")
        asyncio.run(cleanup_loop(args.interval))
    else:
        stats = asyncio.run(run_cleanup())
        print(f"Cleanup completed: {stats}")
