"""
GBP Audit Bot - Grid Router

Endpoints for grid generation and credit estimation.
"""
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models.models import User
from app.schemas import (
    GridGenerateRequest, 
    GridGenerateResponse, 
    GridPointResponse,
    CreditEstimateRequest,
    CreditEstimateResponse
)
from app.services.geogrid import generate_geogrid, estimate_credits


router = APIRouter(prefix="/grid", tags=["Grid"])


@router.post("/generate", response_model=GridGenerateResponse)
async def generate_grid(
    request: GridGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a coordinate grid for visualization.
    
    This endpoint generates the grid points without executing a search.
    Use this for previewing the grid before running a scan.
    """
    points = generate_geogrid(
        center_lat=request.lat,
        center_lng=request.lng,
        radius_km=request.radius_km,
        grid_size=request.grid_size
    )
    
    return GridGenerateResponse(
        points=[
            GridPointResponse(
                x=p.x,
                y=p.y,
                latitude=p.latitude,
                longitude=p.longitude,
                label=p.label
            )
            for p in points
        ],
        total_points=len(points),
        estimated_credits=estimate_credits(request.grid_size)
    )


@router.post("/estimate", response_model=CreditEstimateResponse)
async def estimate_search_credits(
    request: CreditEstimateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Estimate credits required for a grid search.
    
    Call this before executing a search to inform the user
    about the cost and verify they have sufficient credits.
    """
    credits_required = estimate_credits(request.grid_size)
    has_sufficient = current_user.credits_balance >= credits_required
    
    if has_sufficient:
        message = f"Esta busca consumirá {credits_required} créditos."
    else:
        message = f"Créditos insuficientes. Necessário: {credits_required}, Disponível: {current_user.credits_balance}"
    
    return CreditEstimateResponse(
        grid_size=request.grid_size,
        total_points=request.grid_size * request.grid_size,
        credits_required=credits_required,
        user_balance=current_user.credits_balance,
        has_sufficient_credits=has_sufficient,
        message=message
    )
