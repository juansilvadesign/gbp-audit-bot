"""
GBP Audit Bot - Reports Router

Endpoints for generating reports, comparisons, and sending notifications.
"""
import base64
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models.models import User, Project, Scan, ScanPoint
from app.services.geogrid import calculate_scan_stats, get_rank_color
from app.services.heatmap import MapPoint, generate_heatmap_image
from app.services.pdf_report import ReportData, generate_pdf_report
from app.services.ai_analysis import get_ai_analysis, WeeklyStats
from app.services.whatsapp import (
    format_weekly_report_message,
    send_weekly_report,
    WhatsAppMessage,
    send_whatsapp_message
)


router = APIRouter(prefix="/reports", tags=["Reports"])


# ============= Request/Response Schemas =============

class WeeklyComparisonRequest(BaseModel):
    """Request for weekly comparison."""
    project_id: UUID
    include_ai_analysis: bool = True


class WeeklyComparisonResponse(BaseModel):
    """Response with weekly comparison data."""
    business_name: str
    keyword: str
    current_date: str
    previous_date: Optional[str]
    
    # Current metrics
    current_arp: Optional[float]
    current_top3: int
    current_top10: int
    current_visibility: float
    
    # Previous metrics
    prev_arp: Optional[float]
    prev_top3: Optional[int]
    prev_visibility: Optional[float]
    
    # Changes
    arp_change: Optional[float]
    top3_change: Optional[int]
    visibility_change: Optional[float]
    
    # AI analysis
    ai_analysis: Optional[str]


class PDFReportRequest(BaseModel):
    """Request for PDF report generation."""
    project_id: UUID
    scan_id: Optional[UUID] = None  # Latest if not provided
    include_heatmap: bool = True
    include_ai_analysis: bool = True


class WhatsAppReportRequest(BaseModel):
    """Request to send WhatsApp report."""
    project_id: UUID
    group_id: str  # WhatsApp group JID
    heatmap_url: Optional[str] = None
    dashboard_url: Optional[str] = None


# ============= Endpoints =============

@router.post("/comparison", response_model=WeeklyComparisonResponse)
async def get_weekly_comparison(
    request: WeeklyComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get weekly comparison between latest and previous scan.
    
    Optionally includes AI analysis of the results.
    """
    # Get project
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get latest 2 scans
    result = await db.execute(
        select(Scan)
        .where(Scan.project_id == request.project_id, Scan.status == "completed")
        .order_by(Scan.executed_at.desc())
        .limit(2)
    )
    scans = result.scalars().all()
    
    if not scans:
        raise HTTPException(status_code=404, detail="No completed scans found")
    
    current_scan = scans[0]
    prev_scan = scans[1] if len(scans) > 1 else None
    
    total_points = current_scan.grid_size ** 2
    
    # Calculate changes
    arp_change = None
    top3_change = None
    visibility_change = None
    
    if prev_scan:
        if current_scan.average_rank and prev_scan.average_rank:
            arp_change = float(prev_scan.average_rank - current_scan.average_rank)  # Positive = improvement
        top3_change = current_scan.top3_count - prev_scan.top3_count
        if current_scan.visibility_score and prev_scan.visibility_score:
            visibility_change = float(current_scan.visibility_score - prev_scan.visibility_score)
    
    # AI Analysis
    ai_analysis = None
    if request.include_ai_analysis:
        current_stats = WeeklyStats(
            arp=float(current_scan.average_rank) if current_scan.average_rank else None,
            top3=current_scan.top3_count,
            visibility=float(current_scan.visibility_score) if current_scan.visibility_score else 0
        )
        
        prev_stats = None
        if prev_scan:
            prev_stats = WeeklyStats(
                arp=float(prev_scan.average_rank) if prev_scan.average_rank else None,
                top3=prev_scan.top3_count,
                visibility=float(prev_scan.visibility_score) if prev_scan.visibility_score else 0
            )
        
        try:
            ai_analysis = await get_ai_analysis(
                business_name=project.business_name,
                current_stats=current_stats,
                prev_stats=prev_stats,
                actions=project.weekly_actions
            )
        except Exception:
            ai_analysis = None  # Fallback handled in service
    
    return WeeklyComparisonResponse(
        business_name=project.business_name,
        keyword=project.target_keyword,
        current_date=current_scan.executed_at.isoformat(),
        previous_date=prev_scan.executed_at.isoformat() if prev_scan else None,
        current_arp=float(current_scan.average_rank) if current_scan.average_rank else None,
        current_top3=current_scan.top3_count,
        current_top10=current_scan.top10_count,
        current_visibility=float(current_scan.visibility_score) if current_scan.visibility_score else 0,
        prev_arp=float(prev_scan.average_rank) if prev_scan and prev_scan.average_rank else None,
        prev_top3=prev_scan.top3_count if prev_scan else None,
        prev_visibility=float(prev_scan.visibility_score) if prev_scan and prev_scan.visibility_score else None,
        arp_change=arp_change,
        top3_change=top3_change,
        visibility_change=visibility_change,
        ai_analysis=ai_analysis
    )


@router.post("/pdf")
async def generate_pdf(
    request: PDFReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a PDF report for a project.
    
    Returns the PDF file as a download.
    """
    # Get project
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get scan (specific or latest)
    if request.scan_id:
        result = await db.execute(
            select(Scan).where(Scan.id == request.scan_id)
        )
    else:
        result = await db.execute(
            select(Scan)
            .where(Scan.project_id == request.project_id, Scan.status == "completed")
            .order_by(Scan.executed_at.desc())
            .limit(1)
        )
    
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Get scan points for heatmap
    result = await db.execute(
        select(ScanPoint).where(ScanPoint.scan_id == scan.id)
    )
    points = result.scalars().all()
    
    # Get previous scan for comparison
    result = await db.execute(
        select(Scan)
        .where(
            Scan.project_id == request.project_id,
            Scan.status == "completed",
            Scan.executed_at < scan.executed_at
        )
        .order_by(Scan.executed_at.desc())
        .limit(1)
    )
    prev_scan = result.scalar_one_or_none()
    
    total_points = scan.grid_size ** 2
    
    # Generate heatmap image
    heatmap_bytes = None
    if request.include_heatmap and points:
        map_points = [
            MapPoint(
                lat=float(p.latitude),
                lng=float(p.longitude),
                rank=p.rank_position,
                color=get_rank_color(p.rank_position)
            )
            for p in points
        ]
        heatmap_bytes = generate_heatmap_image(map_points)
    
    # Get AI analysis
    ai_analysis = None
    if request.include_ai_analysis:
        current_stats = WeeklyStats(
            arp=float(scan.average_rank) if scan.average_rank else None,
            top3=scan.top3_count,
            visibility=float(scan.visibility_score) if scan.visibility_score else 0
        )
        
        prev_stats = None
        if prev_scan:
            prev_stats = WeeklyStats(
                arp=float(prev_scan.average_rank) if prev_scan.average_rank else None,
                top3=prev_scan.top3_count,
                visibility=float(prev_scan.visibility_score) if prev_scan.visibility_score else 0
            )
        
        try:
            ai_analysis = await get_ai_analysis(
                business_name=project.business_name,
                current_stats=current_stats,
                prev_stats=prev_stats,
                actions=project.weekly_actions
            )
        except Exception:
            pass
    
    # Build report data
    report_data = ReportData(
        business_name=project.business_name,
        keyword=project.target_keyword,
        scan_date=scan.executed_at,
        current_arp=float(scan.average_rank) if scan.average_rank else None,
        current_top3=scan.top3_count,
        current_top10=scan.top10_count,
        current_visibility=float(scan.visibility_score) if scan.visibility_score else 0,
        prev_arp=float(prev_scan.average_rank) if prev_scan and prev_scan.average_rank else None,
        prev_top3=prev_scan.top3_count if prev_scan else None,
        prev_visibility=float(prev_scan.visibility_score) if prev_scan and prev_scan.visibility_score else None,
        grid_size=scan.grid_size,
        total_points=total_points,
        ai_analysis=ai_analysis,
        weekly_actions=project.weekly_actions,
        heatmap_image=heatmap_bytes
    )
    
    # Generate PDF
    pdf_bytes = generate_pdf_report(report_data)
    
    # Return as downloadable file
    filename = f"gbp_report_{project.business_name.replace(' ', '_')}_{scan.executed_at.strftime('%Y%m%d')}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/heatmap/{scan_id}")
async def get_heatmap_image(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and return heatmap image for a scan.
    
    Returns PNG image.
    """
    # Get scan with project for ownership check
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Verify ownership
    result = await db.execute(
        select(Project).where(
            Project.id == scan.project_id,
            Project.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get scan points
    result = await db.execute(
        select(ScanPoint).where(ScanPoint.scan_id == scan_id)
    )
    points = result.scalars().all()
    
    if not points:
        raise HTTPException(status_code=404, detail="No points found for scan")
    
    # Generate heatmap
    map_points = [
        MapPoint(
            lat=float(p.latitude),
            lng=float(p.longitude),
            rank=p.rank_position,
            color=get_rank_color(p.rank_position)
        )
        for p in points
    ]
    
    heatmap_bytes = generate_heatmap_image(map_points)
    
    return Response(
        content=heatmap_bytes,
        media_type="image/png"
    )


class PDFGenerateDirectRequest(BaseModel):
    """Request for direct PDF generation from frontend data."""
    business_name: str
    keyword: str
    scan_date: str  # ISO format date string
    
    # Grid config
    grid_size: int = 5
    radius_km: float = 5.0
    lat: float
    lng: float
    
    # Metrics
    average_rank: float
    visibility_score: float
    top3_count: int
    top10_count: int
    total_points: int
    
    # Optional previous metrics for comparison
    prev_average_rank: Optional[float] = None
    prev_top3_count: Optional[int] = None
    prev_visibility_score: Optional[float] = None
    
    # Optional heatmap image as base64 (PNG)
    heatmap_base64: Optional[str] = None


@router.post("/pdf/generate")
async def generate_pdf_direct(request: PDFGenerateDirectRequest):
    """
    Generate a PDF report from direct data (no auth required).
    
    This endpoint accepts scan data directly from the frontend,
    useful for client-side generated results.
    
    Returns the PDF file as a download.
    """
    # Parse scan date
    try:
        scan_date = datetime.fromisoformat(request.scan_date.replace('Z', '+00:00'))
    except ValueError:
        scan_date = datetime.now()
    
    # Decode heatmap if provided
    heatmap_bytes = None
    if request.heatmap_base64:
        try:
            # Remove data URL prefix if present
            base64_data = request.heatmap_base64
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            heatmap_bytes = base64.b64decode(base64_data)
        except Exception:
            pass  # Skip heatmap if decode fails
    
    # Build report data
    report_data = ReportData(
        business_name=request.business_name,
        keyword=request.keyword,
        scan_date=scan_date,
        current_arp=request.average_rank,
        current_top3=request.top3_count,
        current_top10=request.top10_count,
        current_visibility=request.visibility_score,
        prev_arp=request.prev_average_rank,
        prev_top3=request.prev_top3_count,
        prev_visibility=request.prev_visibility_score,
        grid_size=request.grid_size,
        total_points=request.total_points,
        heatmap_image=heatmap_bytes
    )
    
    # Generate PDF
    pdf_bytes = generate_pdf_report(report_data)
    
    # Return as downloadable file
    safe_name = request.business_name.replace(' ', '_').replace('/', '_')
    filename = f"gbp_report_{safe_name}_{scan_date.strftime('%Y%m%d')}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/whatsapp/send")
async def send_whatsapp_report_endpoint(
    request: WhatsAppReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send weekly report to WhatsApp group.
    
    Requires WhatsApp API configuration in settings.
    """
    # Get project
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get latest 2 scans
    result = await db.execute(
        select(Scan)
        .where(Scan.project_id == request.project_id, Scan.status == "completed")
        .order_by(Scan.executed_at.desc())
        .limit(2)
    )
    scans = result.scalars().all()
    
    if not scans:
        raise HTTPException(status_code=404, detail="No completed scans found")
    
    current_scan = scans[0]
    prev_scan = scans[1] if len(scans) > 1 else None
    
    total_points = current_scan.grid_size ** 2
    
    # Format dates
    period_end = current_scan.executed_at.strftime("%d/%m")
    period_start = (current_scan.executed_at - timedelta(days=7)).strftime("%d/%m")
    
    try:
        response = await send_weekly_report(
            group_id=request.group_id,
            business_name=project.business_name,
            avg_rank=float(current_scan.average_rank) if current_scan.average_rank else 0,
            prev_avg_rank=float(prev_scan.average_rank) if prev_scan and prev_scan.average_rank else None,
            top3_count=current_scan.top3_count,
            total_points=total_points,
            visibility_score=float(current_scan.visibility_score) if current_scan.visibility_score else 0,
            period_start=period_start,
            period_end=period_end,
            heatmap_url=request.heatmap_url,
            dashboard_url=request.dashboard_url
        )
        return {"status": "sent", "response": response}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send WhatsApp message: {str(e)}"
        )


@router.post("/whatsapp/test/{project_id}")
async def test_whatsapp_report(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger a WhatsApp report for testing.
    
    Sends the weekly report immediately for the specified project.
    Requires the project to have whatsapp_group_id configured.
    """
    # Import here to avoid circular imports
    from app.services.scheduler import send_single_project_report
    
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Call the scheduler function
    response = await send_single_project_report(str(project_id))
    
    if response["status"] == "error":
        raise HTTPException(status_code=400, detail=response["message"])
    
    return response

