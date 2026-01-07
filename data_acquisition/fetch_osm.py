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

# Configure osmnx for larger query areas
ox.settings.max_query_area_size = 50000 * 50000  # 50km x 50km


def fetch_buildings(north: float, south: float, east: float, west: float, verbose: bool = False) -> gpd.GeoDataFrame:
    """
    Fetch building footprints from OpenStreetMap for a bounding box.

    Args:
        north: Northern latitude
        south: Southern latitude
        east: Eastern longitude
        west: Western longitude
        verbose: Enable verbose output

    Returns:
        GeoDataFrame with building footprints and metadata
    """
    if verbose:
        print(f"  → Fetching buildings from OSM for bbox: ({south}, {west}) to ({north}, {east})")
        print(f"  → Sending request to Overpass API...")
    else:
        print(f"Fetching buildings from OSM for bbox: ({south}, {west}) to ({north}, {east})")

    try:
        # Fetch building footprints
        # Note: osmnx 2.0+ uses bbox=(north, south, east, west) instead of keyword args
        if verbose:
            print(f"  → Waiting for API response (this may take a while)...")

        buildings = ox.features_from_bbox(
            bbox=(north, south, east, west),
            tags={'building': True}
        )

        if verbose:
            print(f"  → Received response, processing {len(buildings)} features...")

        # Keep only polygon geometries (filter out points and lines)
        buildings = buildings[buildings.geometry.type.isin(['Polygon', 'MultiPolygon'])]

        if verbose:
            print(f"  → Filtered to {len(buildings)} polygon buildings...")

        # Extract useful attributes
        useful_columns = ['geometry', 'building', 'height', 'building:levels',
                         'building:material', 'roof:shape', 'name', 'addr:street']

        # Keep only columns that exist
        columns_to_keep = [col for col in useful_columns if col in buildings.columns]
        buildings = buildings[columns_to_keep].copy()

        # Reset index to get osmid as a column
        buildings = buildings.reset_index()

        # Create a unique building ID
        # Handle various index types in osmnx 2.0+
        if 'osmid' in buildings.columns:
            # Filter out NaN values and convert to string
            buildings['building_id'] = buildings.apply(
                lambda row: f"osm_{int(row['osmid'])}" if pd.notna(row.get('osmid')) else f"osm_{row.name}",
                axis=1
            )
        elif 'element_type' in buildings.columns and 'osmid' in buildings.index.names:
            # Multi-index case
            buildings['building_id'] = buildings.index.get_level_values('osmid').astype(str)
            buildings['building_id'] = 'osm_' + buildings['building_id']
        else:
            # Fallback to row index
            buildings['building_id'] = 'osm_' + buildings.index.astype(str)

        print(f"Retrieved {len(buildings)} buildings")

        return buildings

    except Exception as e:
        print(f"Error fetching buildings: {e}")
        return gpd.GeoDataFrame()


def fetch_roads(north: float, south: float, east: float, west: float, verbose: bool = False) -> gpd.GeoDataFrame:
    """
    Fetch road network from OpenStreetMap for a bounding box.

    Args:
        north: Northern latitude
        south: Southern latitude
        east: Eastern longitude
        west: Western longitude
        verbose: Enable verbose output

    Returns:
        GeoDataFrame with road network
    """
    if verbose:
        print(f"  → Fetching roads from OSM for bbox: ({south}, {west}) to ({north}, {east})")
        print(f"  → Querying road network...")
    else:
        print(f"Fetching roads from OSM for bbox: ({south}, {west}) to ({north}, {east})")

    try:
        # Fetch road network as a graph
        # Note: osmnx 2.0+ uses bbox=(north, south, east, west) instead of keyword args
        if verbose:
            print(f"  → Waiting for road network data...")

        G = ox.graph_from_bbox(
            bbox=(north, south, east, west),
            network_type='drive'
        )

        if verbose:
            print(f"  → Converting graph to GeoDataFrame...")

        # Convert to GeoDataFrame
        roads = ox.graph_to_gdfs(G, nodes=False, edges=True)

        # Keep useful attributes
        useful_columns = ['geometry', 'highway', 'name', 'width', 'lanes', 'surface']
        columns_to_keep = [col for col in useful_columns if col in roads.columns]
        roads = roads[columns_to_keep].copy()

        roads = roads.reset_index()

        print(f"Retrieved {len(roads)} road segments")

        return roads

    except Exception as e:
        print(f"Error fetching roads: {e}")
        return gpd.GeoDataFrame()


def process_building_heights(buildings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Process and estimate building heights from available data.

    Args:
        buildings: GeoDataFrame with building data

    Returns:
        GeoDataFrame with processed height column
    """
    from ..utils.config import DEFAULT_BUILDING_HEIGHT
    from ..utils.geo_utils import estimate_height_from_levels

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
