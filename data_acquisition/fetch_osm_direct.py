"""
Direct Overpass API fetching to bypass OSMnx projection bug
"""
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from typing import Dict, List, Any
import warnings

warnings.filterwarnings('ignore')

OVERPASS_ENDPOINT = "https://overpass.kumi.systems/api/interpreter"
TIMEOUT = 180


def fetch_buildings_direct(north: float, south: float, east: float, west: float, verbose: bool = False) -> gpd.GeoDataFrame:
    """
    Fetch building footprints directly from Overpass API.

    Args:
        north: Northern latitude
        south: Southern latitude
        east: Eastern longitude
        west: Western longitude
        verbose: Enable verbose output

    Returns:
        GeoDataFrame with building footprints
    """
    if verbose:
        print(f"  -> Fetching buildings from bbox: ({south}, {west}) to ({north}, {east})")
        print(f"  -> Using Overpass endpoint: {OVERPASS_ENDPOINT}")

    overpass_query = f"""
[out:json][timeout:{TIMEOUT}];
(
  way["building"]({south},{west},{north},{east});
  relation["building"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    try:
        if verbose:
            print(f"  -> Sending query...")

        response = requests.post(
            OVERPASS_ENDPOINT,
            data={'data': overpass_query},
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return gpd.GeoDataFrame()

        data = response.json()
        elements = data.get('elements', [])

        if verbose:
            print(f"  -> Received {len(elements)} elements")

        # Create lookup for nodes
        nodes = {e['id']: (e['lon'], e['lat']) for e in elements if e['type'] == 'node'}

        # Process ways (buildings)
        buildings_data = []

        for element in elements:
            if element['type'] not in ['way', 'relation']:
                continue

            if 'tags' not in element or 'building' not in element['tags']:
                continue

            # Get geometry
            if element['type'] == 'way':
                if 'nodes' not in element or len(element['nodes']) < 3:
                    continue

                coords = [nodes[nid] for nid in element['nodes'] if nid in nodes]

                if len(coords) < 3:
                    continue

                try:
                    geometry = Polygon(coords)
                except Exception:
                    continue

            else:  # relation - skip for now
                continue

            # Extract tags
            tags = element.get('tags', {})

            building_data = {
                'osmid': element['id'],
                'building': tags.get('building', 'yes'),
                'height': tags.get('height'),
                'building:levels': tags.get('building:levels'),
                'building:material': tags.get('building:material'),
                'roof:shape': tags.get('roof:shape'),
                'name': tags.get('name'),
                'addr:street': tags.get('addr:street'),
                'geometry': geometry
            }

            buildings_data.append(building_data)

        if len(buildings_data) == 0:
            print("No buildings found")
            return gpd.GeoDataFrame()

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(buildings_data, crs='EPSG:4326')

        # Add building_id
        gdf['building_id'] = 'osm_' + gdf['osmid'].astype(str)

        if verbose:
            print(f"  -> Processed {len(gdf)} buildings")

        print(f"Retrieved {len(gdf)} buildings")

        return gdf

    except requests.Timeout:
        print("Error: Request timed out")
        return gpd.GeoDataFrame()
    except Exception as e:
        print(f"Error fetching buildings: {e}")
        import traceback
        traceback.print_exc()
        return gpd.GeoDataFrame()


def fetch_roads_direct(north: float, south: float, east: float, west: float, verbose: bool = False) -> gpd.GeoDataFrame:
    """
    Fetch road network directly from Overpass API.

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
        print(f"  -> Fetching roads from bbox: ({south}, {west}) to ({north}, {east})")

    overpass_query = f"""
[out:json][timeout:{TIMEOUT}];
(
  way["highway"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    try:
        if verbose:
            print(f"  -> Sending query...")

        response = requests.post(
            OVERPASS_ENDPOINT,
            data={'data': overpass_query},
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return gpd.GeoDataFrame()

        data = response.json()
        elements = data.get('elements', [])

        if verbose:
            print(f"  -> Received {len(elements)} elements")

        # Create lookup for nodes
        nodes = {e['id']: (e['lon'], e['lat']) for e in elements if e['type'] == 'node'}

        # Process ways (roads)
        roads_data = []

        for element in elements:
            if element['type'] != 'way':
                continue

            if 'tags' not in element or 'highway' not in element['tags']:
                continue

            if 'nodes' not in element or len(element['nodes']) < 2:
                continue

            coords = [nodes[nid] for nid in element['nodes'] if nid in nodes]

            if len(coords) < 2:
                continue

            try:
                geometry = LineString(coords)
            except Exception:
                continue

            # Extract tags
            tags = element.get('tags', {})

            road_data = {
                'osmid': element['id'],
                'highway': tags.get('highway'),
                'name': tags.get('name'),
                'width': tags.get('width'),
                'lanes': tags.get('lanes'),
                'surface': tags.get('surface'),
                'geometry': geometry
            }

            roads_data.append(road_data)

        if len(roads_data) == 0:
            print("No roads found")
            return gpd.GeoDataFrame()

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(roads_data, crs='EPSG:4326')

        if verbose:
            print(f"  -> Processed {len(gdf)} road segments")

        print(f"Retrieved {len(gdf)} road segments")

        return gdf

    except requests.Timeout:
        print("Error: Request timed out")
        return gpd.GeoDataFrame()
    except Exception as e:
        print(f"Error fetching roads: {e}")
        return gpd.GeoDataFrame()


if __name__ == "__main__":
    # Test with small area
    north, south, east, west = 47.6080, 47.6060, -122.3340, -122.3360

    print("Testing direct Overpass API fetch...")
    print()

    buildings = fetch_buildings_direct(north, south, east, west, verbose=True)
    print()
    print(f"Sample buildings:")
    print(buildings[['building_id', 'building', 'height']].head())
    print()

    roads = fetch_roads_direct(north, south, east, west, verbose=True)
    print()
    if len(roads) > 0:
        print(f"Sample roads:")
        print(roads[['highway', 'name']].head())
