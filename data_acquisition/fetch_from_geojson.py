"""
Load building data from a local GeoJSON file as an alternative to OSM API
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path


def load_buildings_from_geojson(filepath: str, verbose: bool = False) -> gpd.GeoDataFrame:
    """
    Load building footprints from a GeoJSON file.

    This is useful when:
    - OSM Overpass API is down/slow
    - You have pre-downloaded building data
    - You want to use alternative data sources

    Args:
        filepath: Path to GeoJSON file
        verbose: Enable verbose output

    Returns:
        GeoDataFrame with building footprints

    Example GeoJSON sources:
    - Download from Geofabrik: https://download.geofabrik.de/
    - Export from QGIS or similar GIS tools
    - Microsoft Building Footprints: https://github.com/microsoft/USBuildingFootprints
    """
    if verbose:
        print(f"  → Loading buildings from {filepath}")

    try:
        # Read GeoJSON
        buildings = gpd.read_file(filepath)

        if verbose:
            print(f"  → Loaded {len(buildings)} features from file")

        # Filter to only polygon geometries
        buildings = buildings[buildings.geometry.type.isin(['Polygon', 'MultiPolygon'])]

        if verbose:
            print(f"  → Filtered to {len(buildings)} polygon buildings")

        # Ensure we have a building_id column
        if 'building_id' not in buildings.columns:
            if 'id' in buildings.columns:
                buildings['building_id'] = 'bld_' + buildings['id'].astype(str)
            elif 'osm_id' in buildings.columns:
                buildings['building_id'] = 'osm_' + buildings['osm_id'].astype(str)
            else:
                buildings['building_id'] = 'bld_' + buildings.index.astype(str)

        # Try to extract height if available
        height_columns = ['height', 'HEIGHT', 'bld_height', 'building:levels']
        for col in height_columns:
            if col in buildings.columns:
                if verbose:
                    print(f"  → Found height data in column: {col}")
                break

        print(f"Loaded {len(buildings)} buildings from GeoJSON file")

        return buildings

    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return gpd.GeoDataFrame()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        buildings = load_buildings_from_geojson(filepath, verbose=True)
        print(f"\nBuildings loaded: {len(buildings)}")
        if len(buildings) > 0:
            print(f"Columns: {list(buildings.columns)}")
            print(f"\nSample building:")
            print(buildings.iloc[0])
    else:
        print("Usage: py fetch_from_geojson.py <path-to-geojson-file>")
