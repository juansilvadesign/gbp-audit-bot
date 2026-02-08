"""
GBP Audit Bot - Pydantic Schemas for API validation

Request and response models for all API endpoints.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ============= Auth Schemas =============

class UserCreate(BaseModel):
    """Request schema for user registration."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: UUID
    email: str
    name: str
    credits_balance: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


# ============= Project Schemas =============

class ProjectCreate(BaseModel):
    """Request schema for creating a project."""
    business_name: str = Field(..., min_length=2, max_length=255)
    target_keyword: str = Field(..., min_length=2, max_length=255)
    central_lat: float = Field(..., ge=-90, le=90)
    central_lng: float = Field(..., ge=-180, le=180)
    place_id: Optional[str] = None
    default_radius_km: float = Field(default=5.0, gt=0, le=50)
    default_grid_size: int = Field(default=5)
    
    def model_post_init(self, __context):
        if self.default_grid_size not in [3, 5, 7]:
            raise ValueError("Grid size must be 3, 5, or 7")


class ProjectResponse(BaseModel):
    """Response schema for project data."""
    id: UUID
    business_name: str
    target_keyword: str
    central_lat: Decimal
    central_lng: Decimal
    place_id: Optional[str]
    default_radius_km: Decimal
    default_grid_size: int
    weekly_actions: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    """Request schema for updating a project."""
    business_name: Optional[str] = None
    target_keyword: Optional[str] = None
    weekly_actions: Optional[str] = None


# ============= Grid Schemas =============

class GridGenerateRequest(BaseModel):
    """Request schema for generating a coordinate grid."""
    lat: float = Field(..., ge=-90, le=90, description="Central latitude")
    lng: float = Field(..., ge=-180, le=180, description="Central longitude")
    radius_km: float = Field(default=5.0, gt=0, le=50, description="Radius in km")
    grid_size: int = Field(default=5, description="Grid dimension (3, 5, or 7)")
    
    def model_post_init(self, __context):
        if self.grid_size not in [3, 5, 7]:
            raise ValueError("Grid size must be 3, 5, or 7")


class GridPointResponse(BaseModel):
    """Response schema for a single grid point."""
    x: int
    y: int
    latitude: float
    longitude: float
    label: str


class GridGenerateResponse(BaseModel):
    """Response schema for grid generation."""
    points: List[GridPointResponse]
    total_points: int
    estimated_credits: int


# ============= Search/Scan Schemas =============

class SearchExecuteRequest(BaseModel):
    """Request schema for executing a grid search."""
    project_id: UUID
    keyword: Optional[str] = None  # Uses project default if not provided
    radius_km: Optional[float] = Field(default=None, gt=0, le=50)
    grid_size: Optional[int] = None
    
    def model_post_init(self, __context):
        if self.grid_size is not None and self.grid_size not in [3, 5, 7]:
            raise ValueError("Grid size must be 3, 5, or 7")


class CreditEstimateRequest(BaseModel):
    """Request schema for credit estimation."""
    grid_size: int = Field(default=5)
    
    def model_post_init(self, __context):
        if self.grid_size not in [3, 5, 7]:
            raise ValueError("Grid size must be 3, 5, or 7")


class CreditEstimateResponse(BaseModel):
    """Response schema for credit estimation."""
    grid_size: int
    total_points: int
    credits_required: int
    user_balance: int
    has_sufficient_credits: bool
    message: str


class ScanPointResponse(BaseModel):
    """Response schema for a scan point result."""
    grid_x: int
    grid_y: int
    latitude: Decimal
    longitude: Decimal
    rank_position: Optional[int]
    color: str  # green, yellow, red
    
    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    """Response schema for a completed scan."""
    id: UUID
    project_id: UUID
    keyword: str
    grid_size: int
    radius_km: Decimal
    credits_used: int
    average_rank: Optional[Decimal]
    top3_count: int
    top10_count: int
    visibility_score: Optional[Decimal]
    status: str
    executed_at: datetime
    points: List[ScanPointResponse]
    
    class Config:
        from_attributes = True


class ScanSummaryResponse(BaseModel):
    """Summary response for scan list (without all points)."""
    id: UUID
    keyword: str
    grid_size: int
    average_rank: Optional[Decimal]
    top3_count: int
    visibility_score: Optional[Decimal]
    executed_at: datetime
    
    class Config:
        from_attributes = True


# ============= Report Schemas =============

class WeeklyComparisonResponse(BaseModel):
    """Response schema for weekly comparison."""
    business_name: str
    current_scan: ScanSummaryResponse
    previous_scan: Optional[ScanSummaryResponse]
    arp_change: Optional[float]  # Positive = improvement
    top3_change: Optional[int]
    visibility_change: Optional[float]
    ai_analysis: Optional[str]
