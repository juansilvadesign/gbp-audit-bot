"""
GBP Audit Bot - Search Router

Endpoints for executing grid searches and viewing results.
"""
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth import get_current_user
from app.models.models import User, Project, Scan, ScanPoint
from app.schemas import (
    SearchExecuteRequest,
    ScanResponse,
    ScanSummaryResponse,
    ScanPointResponse
)
from app.services.geogrid import (
    generate_geogrid, 
    estimate_credits,
    calculate_scan_stats,
    get_rank_color
)
from app.services.serp import process_grid_search, extract_ranks_from_results


router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/execute", response_model=ScanResponse)
async def execute_search(
    request: SearchExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a grid search for a project.
    
    This will:
    1. Generate the coordinate grid
    2. Call Scale SERP API for each point (with batching)
    3. Calculate metrics (ARP, Top3, Visibility)
    4. Deduct credits from user balance
    5. Save results to database
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Determine search parameters
    keyword = request.keyword or project.target_keyword
    radius_km = request.radius_km or float(project.default_radius_km)
    grid_size = request.grid_size or project.default_grid_size
    
    # Check credits
    credits_required = estimate_credits(grid_size)
    if current_user.credits_balance < credits_required:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Required: {credits_required}, Available: {current_user.credits_balance}"
        )
    
    # Generate grid
    points = generate_geogrid(
        center_lat=float(project.central_lat),
        center_lng=float(project.central_lng),
        radius_km=radius_km,
        grid_size=grid_size
    )
    
    # Create scan record (pending)
    scan = Scan(
        project_id=project.id,
        keyword=keyword,
        grid_size=grid_size,
        radius_km=Decimal(str(radius_km)),
        credits_used=credits_required,
        status="running"
    )
    db.add(scan)
    await db.flush()  # Get scan ID without committing
    
    try:
        # Execute SERP search
        results = await process_grid_search(
            points=points,
            business_name=project.business_name,
            keyword=keyword
        )
        
        # Save scan points
        scan_points = []
        for r in results:
            point = ScanPoint(
                scan_id=scan.id,
                grid_x=r.grid_x,
                grid_y=r.grid_y,
                latitude=Decimal(str(r.latitude)),
                longitude=Decimal(str(r.longitude)),
                rank_position=r.rank_position,
                serp_data=r.serp_data
            )
            scan_points.append(point)
            db.add(point)
        
        # Calculate metrics
        ranks = extract_ranks_from_results(results)
        stats = calculate_scan_stats(ranks, grid_size)
        
        # Update scan with metrics
        scan.average_rank = Decimal(str(stats.arp)) if stats.arp else None
        scan.top3_count = stats.top3
        scan.top10_count = stats.top10
        scan.visibility_score = Decimal(str(stats.visibility_score))
        scan.status = "completed"
        
        # Deduct credits
        current_user.credits_balance -= credits_required
        
        await db.commit()
        await db.refresh(scan)
        
        # Build response
        return ScanResponse(
            id=scan.id,
            project_id=scan.project_id,
            keyword=scan.keyword,
            grid_size=scan.grid_size,
            radius_km=scan.radius_km,
            credits_used=scan.credits_used,
            average_rank=scan.average_rank,
            top3_count=scan.top3_count,
            top10_count=scan.top10_count,
            visibility_score=scan.visibility_score,
            status=scan.status,
            executed_at=scan.executed_at,
            points=[
                ScanPointResponse(
                    grid_x=p.grid_x,
                    grid_y=p.grid_y,
                    latitude=p.latitude,
                    longitude=p.longitude,
                    rank_position=p.rank_position,
                    color=get_rank_color(p.rank_position)
                )
                for p in scan_points
            ]
        )
        
    except Exception as e:
        scan.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search execution failed: {str(e)}"
        )


@router.get("/history/{project_id}", response_model=list[ScanSummaryResponse])
async def get_search_history(
    project_id: UUID,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get search history for a project.
    
    Returns the most recent scans without detailed point data.
    """
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get scans
    result = await db.execute(
        select(Scan)
        .where(Scan.project_id == project_id, Scan.status == "completed")
        .order_by(Scan.executed_at.desc())
        .limit(limit)
    )
    scans = result.scalars().all()
    
    return [
        ScanSummaryResponse(
            id=s.id,
            keyword=s.keyword,
            grid_size=s.grid_size,
            average_rank=s.average_rank,
            top3_count=s.top3_count,
            visibility_score=s.visibility_score,
            executed_at=s.executed_at
        )
        for s in scans
    ]


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan_details(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed results for a specific scan.
    """
    result = await db.execute(
        select(Scan)
        .options(selectinload(Scan.points), selectinload(Scan.project))
        .where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Verify ownership
    if scan.project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ScanResponse(
        id=scan.id,
        project_id=scan.project_id,
        keyword=scan.keyword,
        grid_size=scan.grid_size,
        radius_km=scan.radius_km,
        credits_used=scan.credits_used,
        average_rank=scan.average_rank,
        top3_count=scan.top3_count,
        top10_count=scan.top10_count,
        visibility_score=scan.visibility_score,
        status=scan.status,
        executed_at=scan.executed_at,
        points=[
            ScanPointResponse(
                grid_x=p.grid_x,
                grid_y=p.grid_y,
                latitude=p.latitude,
                longitude=p.longitude,
                rank_position=p.rank_position,
                color=get_rank_color(p.rank_position)
            )
            for p in scan.points
        ]
    )
