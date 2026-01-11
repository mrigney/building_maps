"""
Process road data: calculate widths, generate surface polygons, and standardize materials
"""
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
from typing import Dict, List, Tuple, Optional


# Default road widths by highway type (in meters)
DEFAULT_ROAD_WIDTHS = {
    'motorway': 12.0,      # 3 lanes each direction
    'motorway_link': 8.0,
    'trunk': 10.0,
    'trunk_link': 8.0,
    'primary': 8.0,
    'primary_link': 6.0,
    'secondary': 7.0,
    'secondary_link': 6.0,
    'tertiary': 6.0,
    'tertiary_link': 5.0,
    'unclassified': 5.5,
    'residential': 5.5,
    'living_street': 4.0,
    'service': 4.0,
    'pedestrian': 3.0,
    'track': 3.0,
    'footway': 2.0,
    'bridleway': 2.0,
    'steps': 1.5,
    'path': 1.5,
    'cycleway': 2.0,
}

# Standard lane width (meters)
STANDARD_LANE_WIDTH = 3.5


def calculate_road_width(highway_type: str, width_tag: Optional[str] = None,
                        lanes_tag: Optional[str] = None) -> float:
    """
    Calculate road width from OSM tags.

    Priority:
    1. Explicit width tag (if parseable)
    2. Number of lanes * standard lane width
    3. Default width for highway type

    Args:
        highway_type: OSM highway type (primary, secondary, etc.)
        width_tag: OSM width tag value (e.g., "8", "8m", "8 m")
        lanes_tag: OSM lanes tag value (e.g., "2", "4")

    Returns:
        Road width in meters
    """
    # Try explicit width tag first
    if width_tag:
        try:
            # Handle formats like "8", "8m", "8 m"
            width_str = str(width_tag).lower().replace('m', '').replace(' ', '').strip()
            width = float(width_str)
            if 0.5 <= width <= 50:  # Sanity check (0.5m to 50m)
                return width
        except (ValueError, TypeError):
            pass

    # Try to calculate from number of lanes
    if lanes_tag:
        try:
            lanes = int(lanes_tag)
            if 1 <= lanes <= 12:  # Sanity check
                return lanes * STANDARD_LANE_WIDTH
        except (ValueError, TypeError):
            pass

    # Fall back to default for highway type
    return DEFAULT_ROAD_WIDTHS.get(highway_type, 5.5)  # 5.5m default


def standardize_surface_material(surface_tag: Optional[str], highway_type: str) -> str:
    """
    Standardize OSM surface tag to material category for thermal analysis.

    Args:
        surface_tag: OSM surface tag (e.g., "asphalt", "concrete", "gravel")
        highway_type: OSM highway type (for defaults)

    Returns:
        Standardized material name
    """
    if not surface_tag:
        # Default based on highway type
        if highway_type in ['motorway', 'trunk', 'primary', 'secondary']:
            return 'asphalt_road'
        elif highway_type in ['tertiary', 'residential', 'unclassified']:
            return 'asphalt_road'
        elif highway_type in ['service', 'living_street']:
            return 'asphalt_road'
        elif highway_type in ['footway', 'path', 'pedestrian']:
            return 'concrete_walkway'
        else:
            return 'asphalt_road'

    # Map OSM surface values to standard materials
    surface_lower = str(surface_tag).lower()

    if 'asphalt' in surface_lower:
        return 'asphalt_road'
    elif 'concrete' in surface_lower:
        return 'concrete_road'
    elif 'paving_stone' in surface_lower or 'paved' in surface_lower:
        return 'brick_paved'
    elif 'cobblestone' in surface_lower:
        return 'cobblestone'
    elif 'gravel' in surface_lower:
        return 'gravel'
    elif 'dirt' in surface_lower or 'unpaved' in surface_lower or 'ground' in surface_lower or 'earth' in surface_lower:
        return 'dirt'
    elif 'grass' in surface_lower:
        return 'grass'
    elif 'sand' in surface_lower:
        return 'sand'
    else:
        # Unknown surface - default to asphalt for roads, concrete for walkways
        if highway_type in ['footway', 'path', 'pedestrian']:
            return 'concrete_walkway'
        return 'asphalt_road'


def generate_road_polygon(centerline: LineString, width: float) -> Polygon:
    """
    Generate a road surface polygon from a centerline and width.

    Args:
        centerline: Road centerline geometry (LineString)
        width: Road width in meters

    Returns:
        Polygon representing the road surface
    """
    try:
        # Buffer the centerline by half the width on each side
        # cap_style=2 is flat ends, join_style=2 is mitered joins
        road_polygon = centerline.buffer(width / 2.0, cap_style=2, join_style=2)

        # Ensure it's a Polygon (buffer might return MultiPolygon for complex geometries)
        if isinstance(road_polygon, MultiPolygon):
            # Take the largest polygon
            road_polygon = max(road_polygon.geoms, key=lambda p: p.area)

        return road_polygon

    except Exception as e:
        print(f"Warning: Failed to generate road polygon: {e}")
        # Return a very thin polygon as fallback
        return centerline.buffer(0.1, cap_style=2, join_style=2)


def process_roads_with_surfaces(roads_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Process roads GeoDataFrame to add width, surface polygons, and material info.

    Args:
        roads_gdf: GeoDataFrame with road network data (must have 'geometry' as LineString)

    Returns:
        Enhanced GeoDataFrame with additional columns:
        - width_m: calculated road width
        - surface_material: standardized material name
        - surface_polygon: Polygon geometry for road surface
    """
    if roads_gdf is None or len(roads_gdf) == 0:
        return roads_gdf

    roads = roads_gdf.copy()

    # Calculate widths
    roads['width_m'] = roads.apply(
        lambda row: calculate_road_width(
            highway_type=row.get('highway', 'residential'),
            width_tag=row.get('width'),
            lanes_tag=row.get('lanes')
        ),
        axis=1
    )

    # Standardize surface materials
    roads['surface_material'] = roads.apply(
        lambda row: standardize_surface_material(
            surface_tag=row.get('surface'),
            highway_type=row.get('highway', 'residential')
        ),
        axis=1
    )

    # Generate surface polygons
    print("Generating road surface polygons...")
    roads['surface_polygon'] = roads.apply(
        lambda row: generate_road_polygon(row['geometry'], row['width_m']),
        axis=1
    )

    # Print statistics
    print(f"\nRoad width statistics:")
    print(f"  Min: {roads['width_m'].min():.1f}m")
    print(f"  Max: {roads['width_m'].max():.1f}m")
    print(f"  Mean: {roads['width_m'].mean():.1f}m")

    print(f"\nSurface materials:")
    material_counts = roads['surface_material'].value_counts()
    for material, count in material_counts.items():
        print(f"  {material}: {count}")

    return roads


def convert_road_polygon_to_local_coords(polygon: Polygon, origin_lat: float, origin_lon: float) -> List[Tuple[float, float]]:
    """
    Convert road polygon from lat/lon to local meter coordinates.

    Args:
        polygon: Shapely Polygon in lat/lon coordinates (EPSG:4326)
        origin_lat: Origin latitude for coordinate transformation
        origin_lon: Origin longitude for coordinate transformation

    Returns:
        List of (x, y) tuples in local meter coordinates
    """
    try:
        from ..utils.geo_utils import lat_lon_to_meters
    except ImportError:
        # Fallback for direct script execution
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from utils.geo_utils import lat_lon_to_meters

    # Get exterior coordinates (lon, lat format from Shapely)
    coords = list(polygon.exterior.coords)

    # Convert to local meters
    local_coords = []
    for lon, lat in coords:
        x, y = lat_lon_to_meters(lat, lon, origin_lat, origin_lon)
        local_coords.append((x, y))

    return local_coords


if __name__ == "__main__":
    # Test width calculation
    print("Testing road width calculation:")
    print(f"Primary road with 4 lanes: {calculate_road_width('primary', lanes_tag='4')}m")
    print(f"Secondary road with explicit 7m: {calculate_road_width('secondary', width_tag='7m')}m")
    print(f"Residential road (default): {calculate_road_width('residential')}m")
    print(f"Footway (default): {calculate_road_width('footway')}m")

    print("\nTesting surface material standardization:")
    print(f"asphalt -> {standardize_surface_material('asphalt', 'primary')}")
    print(f"concrete -> {standardize_surface_material('concrete', 'secondary')}")
    print(f"paving_stones -> {standardize_surface_material('paving_stones', 'footway')}")
    print(f"None (primary) -> {standardize_surface_material(None, 'primary')}")
    print(f"None (footway) -> {standardize_surface_material(None, 'footway')}")
