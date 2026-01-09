"""
Geographic utility functions for coordinate transformations and calculations
"""
import numpy as np
from shapely.geometry import Point, Polygon
import geopandas as gpd
from typing import Tuple


def lat_lon_to_meters(lat: float, lon: float, origin_lat: float, origin_lon: float) -> Tuple[float, float]:
    """
    Convert lat/lon to local meters from an origin point.
    Uses simple equirectangular projection for small areas.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        origin_lat: Origin latitude in degrees
        origin_lon: Origin longitude in degrees

    Returns:
        (x, y) in meters from origin
    """
    # Earth radius in meters
    R = 6371000

    # Convert to radians
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    origin_lat_rad = np.radians(origin_lat)
    origin_lon_rad = np.radians(origin_lon)

    # Calculate offsets in meters
    x = R * (lon_rad - origin_lon_rad) * np.cos(origin_lat_rad)
    y = R * (lat_rad - origin_lat_rad)

    return x, y


def polygon_to_local_coords(polygon: Polygon, origin_lat: float, origin_lon: float) -> Polygon:
    """
    Transform a polygon from lat/lon to local meter coordinates.

    Args:
        polygon: Shapely polygon in lat/lon
        origin_lat: Origin latitude
        origin_lon: Origin longitude

    Returns:
        Polygon in local meter coordinates
    """
    exterior_coords = []
    for lon, lat in polygon.exterior.coords:
        x, y = lat_lon_to_meters(lat, lon, origin_lat, origin_lon)
        exterior_coords.append((x, y))

    return Polygon(exterior_coords)


def get_bounding_box_center(north: float, south: float, east: float, west: float) -> Tuple[float, float]:
    """
    Calculate the center point of a bounding box.

    Args:
        north: Northern latitude
        south: Southern latitude
        east: Eastern longitude
        west: Western longitude

    Returns:
        (center_lat, center_lon)
    """
    center_lat = (north + south) / 2
    center_lon = (east + west) / 2
    return center_lat, center_lon


def estimate_height_from_levels(levels) -> float:
    """
    Estimate building height from number of levels/floors.

    Args:
        levels: Number of building levels

    Returns:
        Estimated height in meters
    """
    from .config import HEIGHT_PER_FLOOR

    if levels is None:
        return None

    try:
        levels_float = float(levels)
        if np.isnan(levels_float):
            return None
        return levels_float * HEIGHT_PER_FLOOR
    except (ValueError, TypeError):
        return None
