"""
GBP Audit Bot - Geogrid Calculation Service

Mathematical logic for generating coordinate grids around a central point.
Uses linear approximation suitable for short distances (up to 50km radius).
"""
import math
from dataclasses import dataclass
from typing import List


@dataclass
class GridPoint:
    """
    Represents a single point in the geogrid.
    
    Attributes:
        x: Grid column position (0-indexed, left to right)
        y: Grid row position (0-indexed, top to bottom)
        latitude: Geographic latitude in degrees
        longitude: Geographic longitude in degrees
        label: Human-readable label for the point
    """
    x: int
    y: int
    latitude: float
    longitude: float
    label: str


def generate_geogrid(
    center_lat: float,
    center_lng: float,
    radius_km: float,
    grid_size: int = 5
) -> List[GridPoint]:
    """
    Generate a square grid of coordinates around a center point.
    
    Uses linear approximation for coordinate displacement:
    - Latitude: 1 degree ≈ 111,111 meters (constant)
    - Longitude: 1 degree ≈ 111,111 * cos(latitude) meters (varies by latitude)
    
    This approximation is accurate for distances under 50km from center.
    
    Args:
        center_lat: Central latitude in decimal degrees
        center_lng: Central longitude in decimal degrees
        radius_km: Total radius from center to edge of grid in kilometers
        grid_size: Grid dimension (3, 5, or 7). Creates grid_size × grid_size points.
    
    Returns:
        List of GridPoint objects representing all points in the grid,
        ordered from top-left to bottom-right (row by row).
    
    Raises:
        ValueError: If grid_size is not 3, 5, or 7, or if radius is negative.
    
    Example:
        >>> points = generate_geogrid(-22.9711, -43.1825, 2.0, 3)
        >>> len(points)
        9
        >>> points[4].label  # Center point
        'Ponto_1_1'
    """
    if grid_size not in [3, 5, 7]:
        raise ValueError("Grid size must be 3, 5, or 7")
    
    if radius_km <= 0:
        raise ValueError("Radius must be positive")
    
    if radius_km > 50:
        raise ValueError("Radius must not exceed 50km for accurate calculations")
    
    points: List[GridPoint] = []
    
    # Distance between each point in meters
    # Total diameter = 2 * radius, divided by (grid_size - 1) intervals
    step_distance_m = (radius_km * 2000) / (grid_size - 1)
    
    # Offset from center to reach the edge (in grid units)
    half_size = (grid_size - 1) / 2
    
    # Meters per degree of latitude (constant on Earth)
    METERS_PER_LAT_DEGREE = 111111
    
    # Meters per degree of longitude (varies by latitude)
    meters_per_lng_degree = METERS_PER_LAT_DEGREE * math.cos(math.radians(center_lat))
    
    for row in range(grid_size):
        for col in range(grid_size):
            # Calculate offset in meters from center
            # Positive offset_lat = North, Positive offset_lng = East
            offset_lat_m = (half_size - row) * step_distance_m
            offset_lng_m = (col - half_size) * step_distance_m
            
            # Convert meters to degrees
            delta_lat = offset_lat_m / METERS_PER_LAT_DEGREE
            delta_lng = offset_lng_m / meters_per_lng_degree
            
            # Calculate final coordinates
            new_lat = center_lat + delta_lat
            new_lng = center_lng + delta_lng
            
            points.append(GridPoint(
                x=col,
                y=row,
                latitude=round(new_lat, 6),
                longitude=round(new_lng, 6),
                label=f"Ponto_{row}_{col}"
            ))
    
    return points


def estimate_credits(grid_size: int) -> int:
    """
    Estimate the number of SERP API credits needed for a grid search.
    
    Each grid point requires one API call = one credit.
    
    Args:
        grid_size: Grid dimension (3, 5, or 7)
    
    Returns:
        Number of credits (API calls) required for the search.
    
    Example:
        >>> estimate_credits(3)
        9
        >>> estimate_credits(5)
        25
        >>> estimate_credits(7)
        49
    """
    if grid_size not in [3, 5, 7]:
        raise ValueError("Grid size must be 3, 5, or 7")
    
    return grid_size * grid_size


def calculate_visibility_score(ranks: List[int | None], grid_size: int) -> float:
    """
    Calculate the visibility score for a scan.
    
    The visibility score represents how well the business performs across
    the entire grid. Higher scores indicate better local visibility.
    
    Formula: (max_possible_points - total_rank_sum) / max_possible_points * 100
    
    - Best case (all rank 1): score = 100%
    - Worst case (all not found): score = 0%
    
    Args:
        ranks: List of rank positions (None = not found, treated as position 20)
        grid_size: Grid dimension for calculating max points
    
    Returns:
        Visibility score as a percentage (0-100).
    
    Example:
        >>> calculate_visibility_score([1, 1, 1, 2, 2, 2, 3, 3, 3], 3)
        95.0  # Excellent visibility
    """
    total_points = grid_size * grid_size
    max_score = total_points * 20  # 20 is the max rank we track
    
    # Sum of all ranks (None = not found = 20)
    rank_sum = sum(rank if rank is not None else 20 for rank in ranks)
    
    # Calculate score (invert so higher is better)
    score = ((max_score - rank_sum) / (max_score - total_points)) * 100
    
    return round(max(0, min(100, score)), 2)


def calculate_average_rank(ranks: List[int | None]) -> float | None:
    """
    Calculate the average rank position across all grid points.
    
    Only includes points where the business was found (rank is not None).
    
    Args:
        ranks: List of rank positions (None = not found)
    
    Returns:
        Average rank position, or None if business wasn't found anywhere.
    
    Example:
        >>> calculate_average_rank([1, 2, 3, None, 5])
        2.75
    """
    valid_ranks = [r for r in ranks if r is not None]
    
    if not valid_ranks:
        return None
    
    return round(sum(valid_ranks) / len(valid_ranks), 2)


def get_rank_color(rank: int | None) -> str:
    """
    Get the display color for a rank position.
    
    Color coding:
    - Green: Positions 1-3 (Local Pack / Dominance)
    - Yellow: Positions 4-10 (Visible but outside Local Pack)
    - Red: Positions 11+ or not found (Invisible to most users)
    
    Args:
        rank: Rank position (1-20) or None if not found
    
    Returns:
        Color name: 'green', 'yellow', or 'red'
    """
    if rank is None or rank > 10:
        return "red"
    if rank <= 3:
        return "green"
    return "yellow"


def count_top3(ranks: List[int | None]) -> int:
    """
    Count how many grid points have the business in top 3 positions.
    
    This is a key KPI from the esqueleto.md - measures local dominance.
    
    Args:
        ranks: List of rank positions (None = not found)
    
    Returns:
        Number of points where rank is 1, 2, or 3.
    
    Example:
        >>> count_top3([1, 2, 3, 5, 8, None])
        3
    """
    return len([r for r in ranks if r is not None and r <= 3])


def count_top10(ranks: List[int | None]) -> int:
    """
    Count how many grid points have the business in top 10 positions.
    
    Args:
        ranks: List of rank positions (None = not found)
    
    Returns:
        Number of points where rank is 1-10.
    """
    return len([r for r in ranks if r is not None and r <= 10])


@dataclass
class ScanStats:
    """
    Scan statistics as defined in esqueleto.md.
    
    Attributes:
        arp: Average Rank Position (ARP)
        top3: Count of positions in top 3
        top10: Count of positions in top 10
        visibility_score: Overall visibility percentage
        total_points: Total grid points scanned
    """
    arp: float | None
    top3: int
    top10: int
    visibility_score: float
    total_points: int


def calculate_scan_stats(ranks: List[int | None], grid_size: int) -> ScanStats:
    """
    Calculate all scan statistics for a completed grid search.
    
    This matches the metrics format expected by esqueleto.md for
    comparison with previous weeks and AI analysis.
    
    Args:
        ranks: List of rank positions for each grid point
        grid_size: Grid dimension (3, 5, or 7)
    
    Returns:
        ScanStats object with all metrics.
    
    Example:
        >>> stats = calculate_scan_stats([1, 2, 3, 5, 8, 10, 12, None, None], 3)
        >>> stats.arp
        5.86
        >>> stats.top3
        3
    """
    return ScanStats(
        arp=calculate_average_rank(ranks),
        top3=count_top3(ranks),
        top10=count_top10(ranks),
        visibility_score=calculate_visibility_score(ranks, grid_size),
        total_points=grid_size * grid_size
    )

