"""
GBP Audit Bot - Scale SERP API Integration

Async client for fetching local search rankings from Scale SERP API.
Implements batching strategy from api-serp.md to avoid rate limiting.
"""
import asyncio
from dataclasses import dataclass
from typing import List, Optional
import httpx

from app.config import get_settings
from app.services.geogrid import GridPoint


settings = get_settings()


@dataclass
class RankResult:
    """Result of a single grid point search."""
    grid_x: int
    grid_y: int
    latitude: float
    longitude: float
    rank_position: Optional[int]  # None if not found in top 20
    serp_data: Optional[dict]  # Raw API response for debugging


async def fetch_rank_at_point(
    client: httpx.AsyncClient,
    point: GridPoint,
    business_name: str,
    keyword: str,
    api_key: str
) -> RankResult:
    """
    Fetch the rank of a business at a specific coordinate.
    
    Uses Scale SERP API with geo-targeted search.
    
    Args:
        client: Reusable httpx async client
        point: Grid point with coordinates
        business_name: Name of the business to find
        keyword: Search query 
        api_key: Scale SERP API key
    
    Returns:
        RankResult with position and raw data
    """
    params = {
        "api_key": api_key,
        "q": keyword,
        "location": f"geo:{point.latitude},{point.longitude}",
        "google_domain": "google.com.br",
        "gl": "br",
        "hl": "pt",
        "num": 20,  # Get top 20 results
        "output": "json"
    }
    
    try:
        response = await client.get(
            settings.scale_serp_base_url,
            params=params,
            timeout=30.0
        )
        
        if response.status_code != 200:
            return RankResult(
                grid_x=point.x,
                grid_y=point.y,
                latitude=point.latitude,
                longitude=point.longitude,
                rank_position=None,
                serp_data={"error": f"API returned {response.status_code}"}
            )
        
        data = response.json()
        
        # Search in local results first (Google Maps / Local Pack)
        rank_position = _find_business_in_results(
            data.get("local_results", []),
            business_name
        )
        
        # If not in local results, check organic results
        if rank_position is None:
            rank_position = _find_business_in_results(
                data.get("organic_results", []),
                business_name
            )
        
        return RankResult(
            grid_x=point.x,
            grid_y=point.y,
            latitude=point.latitude,
            longitude=point.longitude,
            rank_position=rank_position,
            serp_data=data
        )
        
    except Exception as e:
        return RankResult(
            grid_x=point.x,
            grid_y=point.y,
            latitude=point.latitude,
            longitude=point.longitude,
            rank_position=None,
            serp_data={"error": str(e)}
        )


def _find_business_in_results(results: List[dict], business_name: str) -> Optional[int]:
    """
    Find a business in SERP results by name matching.
    
    Uses case-insensitive partial matching.
    
    Args:
        results: List of SERP result items
        business_name: Name to search for
    
    Returns:
        1-indexed position if found, None otherwise
    """
    business_lower = business_name.lower()
    
    for idx, result in enumerate(results):
        title = result.get("title", "").lower()
        # Also check 'name' field used in some local results
        name = result.get("name", "").lower()
        
        if business_lower in title or business_lower in name:
            return idx + 1  # 1-indexed position
    
    return None


async def process_grid_search(
    points: List[GridPoint],
    business_name: str,
    keyword: str,
    api_key: Optional[str] = None
) -> List[RankResult]:
    """
    Process a full grid search with async batching.
    
    Follows the optimization strategy from api-serp.md:
    - Uses httpx for async requests
    - Batches requests in groups of 5 to avoid rate limiting
    - Adds small delay between batches
    
    Args:
        points: List of GridPoint from generate_geogrid()
        business_name: Business name to search for
        keyword: Search keyword
        api_key: Scale SERP API key (uses settings if not provided)
    
    Returns:
        List of RankResult for each grid point
    """
    key = api_key or settings.scale_serp_api_key
    
    if not key:
        raise ValueError("Scale SERP API key is required")
    
    results: List[RankResult] = []
    batch_size = settings.serp_batch_size
    delay = settings.serp_batch_delay_seconds
    
    async with httpx.AsyncClient() as client:
        # Process in batches
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            
            # Create tasks for this batch
            tasks = [
                fetch_rank_at_point(client, point, business_name, keyword, key)
                for point in batch
            ]
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            # Add delay between batches (except after last batch)
            if i + batch_size < len(points):
                await asyncio.sleep(delay)
    
    return results


def extract_ranks_from_results(results: List[RankResult]) -> List[Optional[int]]:
    """
    Extract just the rank positions from results for metric calculations.
    
    Args:
        results: List of RankResult from process_grid_search()
    
    Returns:
        List of rank positions (None for not found)
    """
    return [r.rank_position for r in results]
