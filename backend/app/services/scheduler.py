"""
GBP Audit Bot - Scheduler Service

APScheduler-based task scheduler for automated weekly WhatsApp reports.
Runs every Monday at the configured time (default: 9:00 AM Sao Paulo).
"""
import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.models import Project, Scan, ScanPoint
from app.services.whatsapp import send_weekly_report
from app.services.geogrid import get_rank_color
from app.services.heatmap import MapPoint, generate_heatmap_image

logger = logging.getLogger(__name__)
settings = get_settings()

# Global scheduler instance
scheduler: AsyncIOScheduler = None


def init_scheduler() -> AsyncIOScheduler:
    """Initialize and start the scheduler."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return scheduler
    
    scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)
    
    # Add weekly report job
    trigger = CronTrigger(
        day_of_week=settings.weekly_report_day,
        hour=settings.weekly_report_hour,
        minute=settings.weekly_report_minute,
        timezone=settings.scheduler_timezone
    )
    
    scheduler.add_job(
        send_all_weekly_reports,
        trigger=trigger,
        id="weekly_whatsapp_reports",
        name="Send Weekly WhatsApp Reports",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(
        f"Scheduler started. Weekly reports scheduled for {settings.weekly_report_day} "
        f"at {settings.weekly_report_hour:02d}:{settings.weekly_report_minute:02d} "
        f"({settings.scheduler_timezone})"
    )
    
    return scheduler


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Scheduler shutdown complete")


async def send_all_weekly_reports():
    """
    Main scheduled job: send weekly reports to all enabled projects.
    
    This function:
    1. Fetches all projects with whatsapp_enabled=True
    2. For each project, gets the latest 2 scans
    3. Generates heatmap image from latest scan
    4. Sends formatted report via WhatsApp
    """
    logger.info("Starting weekly WhatsApp report job...")
    
    if not settings.whatsapp_api_url or not settings.whatsapp_api_key:
        logger.error("WhatsApp API not configured. Skipping weekly reports.")
        return
    
    async with AsyncSessionLocal() as db:
        # Fetch all projects with WhatsApp enabled
        result = await db.execute(
            select(Project).where(
                Project.whatsapp_enabled == True,
                Project.whatsapp_group_id.isnot(None)
            )
        )
        projects = result.scalars().all()
        
        if not projects:
            logger.info("No projects with WhatsApp enabled. Skipping.")
            return
        
        logger.info(f"Found {len(projects)} project(s) with WhatsApp enabled")
        
        success_count = 0
        error_count = 0
        
        for project in projects:
            try:
                await send_project_report(db, project)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send report for project {project.id}: {e}")
                error_count += 1
        
        logger.info(
            f"Weekly report job completed. Success: {success_count}, Errors: {error_count}"
        )


async def send_project_report(db: AsyncSession, project: Project):
    """Send weekly report for a single project."""
    logger.info(f"Sending report for project: {project.business_name}")
    
    # Get latest 2 scans
    result = await db.execute(
        select(Scan)
        .where(Scan.project_id == project.id, Scan.status == "completed")
        .order_by(Scan.executed_at.desc())
        .limit(2)
    )
    scans = result.scalars().all()
    
    if not scans:
        logger.warning(f"No completed scans for project {project.id}. Skipping.")
        return
    
    current_scan = scans[0]
    prev_scan = scans[1] if len(scans) > 1 else None
    total_points = current_scan.grid_size ** 2
    
    # Get scan points for heatmap
    result = await db.execute(
        select(ScanPoint).where(ScanPoint.scan_id == current_scan.id)
    )
    points = result.scalars().all()
    
    # Generate heatmap URL (if we have points)
    heatmap_url = None
    # Note: For image in WhatsApp, you'd need to upload the image to a public URL
    # or use base64 encoding depending on your gateway's capabilities
    
    # Format dates
    period_end = current_scan.executed_at.strftime("%d/%m")
    period_start = (current_scan.executed_at - timedelta(days=7)).strftime("%d/%m")
    
    # Dashboard URL (replace with actual URL)
    dashboard_url = f"https://your-app.com/scan/{current_scan.id}"
    
    # Send report
    await send_weekly_report(
        group_id=project.whatsapp_group_id,
        business_name=project.business_name,
        avg_rank=float(current_scan.average_rank) if current_scan.average_rank else 0,
        prev_avg_rank=float(prev_scan.average_rank) if prev_scan and prev_scan.average_rank else None,
        top3_count=current_scan.top3_count,
        total_points=total_points,
        visibility_score=float(current_scan.visibility_score) if current_scan.visibility_score else 0,
        period_start=period_start,
        period_end=period_end,
        heatmap_url=heatmap_url,
        insight=project.weekly_actions,
        dashboard_url=dashboard_url,
        api_url=settings.whatsapp_api_url,
        api_key=settings.whatsapp_api_key
    )
    
    logger.info(f"Report sent successfully for: {project.business_name}")


async def send_single_project_report(project_id: str) -> dict:
    """
    Manually trigger a WhatsApp report for a specific project.
    Useful for testing or on-demand reports.
    
    Returns:
        dict with status and message
    """
    if not settings.whatsapp_api_url or not settings.whatsapp_api_key:
        return {"status": "error", "message": "WhatsApp API not configured"}
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        if not project.whatsapp_group_id:
            return {"status": "error", "message": "No WhatsApp group configured for this project"}
        
        try:
            await send_project_report(db, project)
            return {"status": "success", "message": f"Report sent to {project.business_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
