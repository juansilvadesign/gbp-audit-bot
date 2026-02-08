"""
GBP Audit Bot - SQLAlchemy Models

Database schema for the GBP Audit Bot system:
- Users: Authentication and credit management
- Projects: Client businesses being monitored
- Scans: Search history with grid parameters
- ScanPoints: Individual grid point results
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    String, Integer, DateTime, Numeric, ForeignKey, JSON, Text, Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    """
    Users table for authentication and credit management.
    Each user has a credit balance for API calls.
    """
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    credits_balance: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """
    Projects represent client businesses being monitored.
    Each project has a target keyword and business to track.
    """
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Business info
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    place_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Center coordinates
    central_lat: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    central_lng: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    
    # Default grid settings
    default_radius_km: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=5.0)
    default_grid_size: Mapped[int] = mapped_column(Integer, default=5)
    
    # Actions tracking for AI reports (as per esqueleto.md)
    weekly_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Team actions for AI context
    
    # WhatsApp integration
    whatsapp_group_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # JID: 123456789@g.us
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="projects")
    scans: Mapped[List["Scan"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Scan(Base):
    """
    Scans represent a complete grid search execution.
    Stores the grid parameters and aggregate metrics like average rank.
    """
    __tablename__ = "scans"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # Search parameters
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    grid_size: Mapped[int] = mapped_column(Integer, nullable=False)  # 3, 5, or 7
    radius_km: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    
    # Metrics (calculated after scan completes) - matching esqueleto.md
    credits_used: Mapped[int] = mapped_column(Integer, nullable=False)
    average_rank: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # ARP
    top3_count: Mapped[int] = mapped_column(Integer, default=0)  # Count of positions in top 3
    top10_count: Mapped[int] = mapped_column(Integer, default=0)  # Count of positions in top 10
    visibility_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, running, completed, failed
    
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="scans")
    points: Mapped[List["ScanPoint"]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class ScanPoint(Base):
    """
    Individual grid point results.
    Each point stores its coordinates and the rank found at that location.
    """
    __tablename__ = "scan_points"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id"), nullable=False)
    
    # Grid position (0-indexed)
    grid_x: Mapped[int] = mapped_column(Integer, nullable=False)
    grid_y: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Coordinates
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    
    # Results
    rank_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # NULL if not found in top 20
    serp_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Raw API response
    
    # Relationships
    scan: Mapped["Scan"] = relationship(back_populates="points")
    
    @property
    def status_color(self) -> str:
        """Get color based on rank position."""
        if self.rank_position is None:
            return "red"
        if self.rank_position <= 3:
            return "green"
        if self.rank_position <= 10:
            return "yellow"
        return "red"
