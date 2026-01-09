"""
Fetch building and road data from OpenStreetMap
"""
import osmnx as ox
import geopandas as gpd
import pandas as pd
from typing import Tuple, Optional
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure osmnx for larger query areas and use working Overpass server
ox.settings.max_query_area_size = 50000 * 50000  # 50km x 50km
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api/interpreter"
ox.settings.timeout = 180


def fetch_buildings(north: float, south: float, east: float, west: float, verbose: bool = False) -> gpd.GeoDataFrame:
    """
    Fetch building footprints from OpenStreetMap for a bounding box.
    Uses direct Overpass API to avoid OSMnx projection bugs.

    Args:
        north: Northern latitude
        south: Southern latitude
        east: Eastern longitude
        west: Western longitude
        verbose: Enable verbose output

    Returns:
        GeoDataFrame with building footprints and metadata
    """
    # Use direct Overpass API implementation to avoid OSMnx projection bugs
    from .fetch_osm_direct import fetch_buildings_direct
    return fetch_buildings_direct(north, south, east, west, verbose)


def fetch_roads(north: float, south: float, east: float, west: float, verbose: bool = False) -> gpd.GeoDataFrame:
    """
    Fetch road network from OpenStreetMap for a bounding box.
    Uses direct Overpass API to avoid OSMnx projection bugs.

    Args:
        north: Northern latitude
        south: Southern latitude
        east: Eastern longitude
        west: Western longitude
        verbose: Enable verbose output

    Returns:
        GeoDataFrame with road network
    """
    # Use direct Overpass API implementation to avoid OSMnx projection bugs
    from .fetch_osm_direct import fetch_roads_direct
    return fetch_roads_direct(north, south, east, west, verbose)


def process_building_heights(buildings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Process and estimate building heights from available data.

    Args:
        buildings: GeoDataFrame with building data

    Returns:
        GeoDataFrame with processed height column
    """
    try:
        from ..utils.config import DEFAULT_BUILDING_HEIGHT
        from ..utils.geo_utils import estimate_height_from_levels
    except ImportError:
        # Fallback for direct script execution
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from utils.config import DEFAULT_BUILDING_HEIGHT
        from utils.geo_utils import estimate_height_from_levels

    buildings = buildings.copy()

    # Initialize height column
    buildings['height_m'] = None

    # Try to parse explicit height values
    if 'height' in buildings.columns:
        for idx, row in buildings.iterrows():
            if pd.notna(row['height']):
                try:
                    # Handle various formats: "10", "10 m", "10m"
                    height_str = str(row['height']).lower().replace('m', '').strip()
                    buildings.loc[idx, 'height_m'] = float(height_str)
                except (ValueError, TypeError):
                    pass

    # Estimate from building levels
    if 'building:levels' in buildings.columns:
        for idx, row in buildings.iterrows():
            if pd.isna(buildings.loc[idx, 'height_m']) and pd.notna(row['building:levels']):
                estimated = estimate_height_from_levels(row['building:levels'])
                if estimated:
                    buildings.loc[idx, 'height_m'] = estimated

    # Apply default height for remaining buildings
    buildings['height_m'] = buildings['height_m'].fillna(DEFAULT_BUILDING_HEIGHT)

    print(f"Height statistics: min={buildings['height_m'].min():.1f}m, "
          f"max={buildings['height_m'].max():.1f}m, "
          f"mean={buildings['height_m'].mean():.1f}m")

    return buildings


if __name__ == "__main__":
    # Test with a small area in downtown Seattle
    north, south, east, west = 47.6097, 47.6047, -122.3320, -122.3420

    buildings = fetch_buildings(north, south, east, west)
    buildings = process_building_heights(buildings)

    print(f"\nSample building data:")
    print(buildings[['building_id', 'building', 'height_m']].head())

    roads = fetch_roads(north, south, east, west)
    print(f"\nSample road data:")
    print(roads[['highway', 'name']].head() if len(roads) > 0 else "No roads found")
