"""
GBP Audit Bot - Heatmap Image Generator

Generates visual heatmap images for reports using staticmap and Pillow.
Based on mapadecalor.md specifications.
"""
import io
from typing import List, Optional, Tuple
from dataclasses import dataclass

from staticmap import StaticMap, CircleMarker
from PIL import Image, ImageDraw, ImageFont


@dataclass
class MapPoint:
    """A point to render on the heatmap."""
    lat: float
    lng: float
    rank: Optional[int]
    color: str  # hex color


def get_rank_color_hex(rank: Optional[int]) -> str:
    """Get hex color for a rank position."""
    if rank is None or rank > 10:
        return "#ef4444"  # Red
    if rank <= 3:
        return "#22c55e"  # Green
    return "#eab308"  # Yellow


def generate_heatmap_image(
    points: List[MapPoint],
    width: int = 800,
    height: int = 800,
    show_ranks: bool = True
) -> bytes:
    """
    Generate a heatmap image from grid points.
    
    Args:
        points: List of MapPoint with coordinates and rank
        width: Image width in pixels
        height: Image height in pixels
        show_ranks: Whether to draw rank numbers on markers
    
    Returns:
        PNG image as bytes
    """
    # Create the static map
    m = StaticMap(width, height, url_template='https://a.tile.openstreetmap.org/{z}/{x}/{y}.png')
    
    # Add circle markers for each point
    for p in points:
        marker = CircleMarker(
            (p.lng, p.lat),  # Note: staticmap uses (lng, lat) order
            p.color,
            24  # marker radius
        )
        m.add_marker(marker)
    
    # Render the map
    image = m.render()
    
    if show_ranks:
        # Draw rank numbers on top of markers
        image = _draw_rank_labels(image, points, m)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG', optimize=True)
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


def _draw_rank_labels(
    image: Image.Image,
    points: List[MapPoint],
    static_map: StaticMap
) -> Image.Image:
    """Draw rank numbers centered on each marker."""
    draw = ImageDraw.Draw(image)
    
    # Try to load a bold font, fall back to default
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except (IOError, OSError):
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        except (IOError, OSError):
            font = ImageFont.load_default()
    
    for p in points:
        if p.rank is None:
            continue
        
        # Convert lat/lng to pixel coordinates
        try:
            x, y = _latlon_to_pixels(p.lat, p.lng, static_map)
        except Exception:
            continue
        
        # Draw the rank number centered on the marker
        text = str(p.rank)
        
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = x - text_width / 2
        text_y = y - text_height / 2
        
        # Draw text with outline for visibility
        outline_color = "#000000"
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((text_x + dx, text_y + dy), text, font=font, fill=outline_color)
        
        draw.text((text_x, text_y), text, font=font, fill="#ffffff")
    
    return image


def _latlon_to_pixels(lat: float, lng: float, static_map: StaticMap) -> Tuple[int, int]:
    """Convert latitude/longitude to pixel coordinates on the rendered map."""
    import math
    
    # Get map center and zoom from staticmap internals
    center = static_map.determine_extent()
    zoom = center[2]
    center_lat = (center[0][0] + center[1][0]) / 2
    center_lng = (center[0][1] + center[1][1]) / 2
    
    # Mercator projection
    def lat_to_y(lat):
        return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    
    def lng_to_x(lng):
        return math.radians(lng)
    
    # Calculate pixel offset from center
    scale = 256 * (2 ** zoom)
    
    center_x = (lng_to_x(center_lng) + math.pi) / (2 * math.pi) * scale
    center_y = (1 - lat_to_y(center_lat) / math.pi) / 2 * scale
    
    point_x = (lng_to_x(lng) + math.pi) / (2 * math.pi) * scale
    point_y = (1 - lat_to_y(lat) / math.pi) / 2 * scale
    
    # Offset from center of image
    x = static_map.width / 2 + (point_x - center_x)
    y = static_map.height / 2 + (point_y - center_y)
    
    return int(x), int(y)


def save_heatmap_to_file(points: List[MapPoint], filepath: str) -> str:
    """Generate and save heatmap to a file."""
    img_bytes = generate_heatmap_image(points)
    with open(filepath, 'wb') as f:
        f.write(img_bytes)
    return filepath
