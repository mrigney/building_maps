"""
Generate spatial manifest and index files for the urban terrain
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


def process_roads_data(roads_gdf, origin_lat: float = None, origin_lon: float = None) -> dict:
    """
    Process roads GeoDataFrame into manifest-ready format with enhanced data.

    Args:
        roads_gdf: GeoDataFrame with road network data
        origin_lat: Origin latitude for coordinate reference
        origin_lon: Origin longitude for coordinate reference

    Returns:
        Dictionary of road data ready for manifest
    """
    if roads_gdf is None or len(roads_gdf) == 0:
        return {}

    # Process roads to add width, polygons, and materials
    try:
        try:
            from ..geometry.process_roads import (
                process_roads_with_surfaces,
                convert_road_polygon_to_local_coords
            )
        except (ImportError, ValueError):
            # Fallback for direct script execution
            import sys
            from pathlib import Path as PathLib
            sys.path.insert(0, str(PathLib(__file__).parent.parent))
            from geometry.process_roads import (
                process_roads_with_surfaces,
                convert_road_polygon_to_local_coords
            )

        # Enhance road data with calculated widths and surface polygons
        roads_enhanced = process_roads_with_surfaces(roads_gdf)
    except Exception as e:
        print(f"Warning: Could not enhance road data: {e}")
        # Fall back to basic processing
        roads_enhanced = roads_gdf

    roads_dict = {}

    for idx, road in roads_enhanced.iterrows():
        # Create road ID
        road_id = f"road_{idx}"
        if 'osmid' in road and not pd.isna(road['osmid']):
            try:
                road_id = f"osm_road_{int(road['osmid'])}"
            except (ValueError, TypeError):
                pass

        # Extract centerline geometry coordinates
        geom = road['geometry']
        if geom.geom_type == 'LineString':
            coords = [[point[1], point[0]] for point in geom.coords]  # [lat, lon]
        else:
            # Skip non-linestring geometries
            continue

        # Extract road properties
        highway_type = road.get('highway', 'unknown')
        name = road.get('name', None)

        # Get enhanced properties if available
        width_m = road.get('width_m', None)
        surface_material = road.get('surface_material', None)

        # Original OSM tags
        width_tag = road.get('width', None)
        lanes = road.get('lanes', None)
        surface = road.get('surface', None)

        # Build road entry
        road_entry = {
            'type': highway_type,
            'name': name,
            'coordinates': coords,  # Centerline as [lat, lon] pairs
            'properties': {
                'width_m': width_m,  # Calculated width in meters
                'surface_material': surface_material,  # Standardized material
                'osm_tags': {
                    'width': width_tag,
                    'lanes': lanes,
                    'surface': surface
                }
            }
        }

        # Add surface polygon in local coordinates if available
        if 'surface_polygon' in road and road['surface_polygon'] is not None and origin_lat and origin_lon:
            try:
                polygon_coords = convert_road_polygon_to_local_coords(
                    road['surface_polygon'],
                    origin_lat,
                    origin_lon
                )
                road_entry['surface_polygon_local_m'] = polygon_coords
            except Exception as e:
                print(f"Warning: Could not convert road polygon to local coords: {e}")

        roads_dict[road_id] = road_entry

    return roads_dict


def create_manifest(
    buildings_manifest: Dict[str, dict],
    roads_data: dict = None,
    bounding_box: Tuple[float, float, float, float] = None,
    origin: Tuple[float, float] = None,
    output_path: str = None
) -> dict:
    """
    Create a comprehensive manifest file for the urban terrain.

    Args:
        buildings_manifest: Dictionary from export_buildings
        roads_data: Optional road network data (dict or GeoDataFrame)
        bounding_box: (north, south, east, west) in degrees
        origin: (origin_lat, origin_lon) for local coordinate system
        output_path: Path to save manifest JSON

    Returns:
        Manifest dictionary
    """
    # Process roads if GeoDataFrame provided
    if roads_data is not None and not isinstance(roads_data, dict):
        try:
            roads_data = process_roads_data(
                roads_data,
                origin_lat=origin[0] if origin else None,
                origin_lon=origin[1] if origin else None
            )
        except Exception as e:
            print(f"Warning: Could not process roads data: {e}")
            roads_data = {}

    manifest = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'generator': 'urban-terrain-generator v0.2',
            'coordinate_system': {
                'type': 'local_meters',
                'origin_lat': origin[0] if origin else None,
                'origin_lon': origin[1] if origin else None,
                'description': 'Local coordinate system with origin at specified lat/lon, +X = East, +Y = North, +Z = Up'
            },
            'bounding_box': {
                'north': bounding_box[0] if bounding_box else None,
                'south': bounding_box[1] if bounding_box else None,
                'east': bounding_box[2] if bounding_box else None,
                'west': bounding_box[3] if bounding_box else None
            } if bounding_box else None
        },
        'statistics': {
            'total_buildings': len(buildings_manifest),
            'unique_models': len(set(
                b.get('prototype', b['filename']) for b in buildings_manifest.values()
            )),
            'total_roads': len(roads_data) if roads_data else 0
        },
        'buildings': {},
        'roads': roads_data if roads_data else {}
    }

    # Process building data
    for building_id, building_info in buildings_manifest.items():
        metadata = building_info.get('metadata', {})

        manifest['buildings'][building_id] = {
            'model_file': building_info['filename'],
            'is_instance': building_info.get('is_instance', False),
            'prototype': building_info.get('prototype', None),
            'position': {
                'lat': metadata.get('centroid_lat'),
                'lon': metadata.get('centroid_lon')
            },
            'properties': {
                'height_m': metadata.get('height'),
                'building_type': metadata.get('building_type'),
                'area_sqm': metadata.get('area_sqm')
            }
        }

    # Save to file if path provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"Manifest saved to {output_path}")

    return manifest


def create_spatial_index(
    buildings_manifest: Dict[str, dict],
    grid_size: float = 100.0
) -> Dict[str, List[str]]:
    """
    Create a spatial grid index for efficient queries.

    Args:
        buildings_manifest: Dictionary from export_buildings
        grid_size: Size of grid cells in meters

    Returns:
        Dictionary mapping grid cell IDs to lists of building IDs
    """
    spatial_index = {}

    for building_id, building_info in buildings_manifest.items():
        metadata = building_info.get('metadata', {})

        # Get position (approximate for now - would need proper conversion)
        lat = metadata.get('centroid_lat', 0)
        lon = metadata.get('centroid_lon', 0)

        # Simple grid assignment (in lat/lon space - would be better in meters)
        grid_x = int(lon / (grid_size / 111320))  # Approximate degrees per meter
        grid_y = int(lat / (grid_size / 111320))

        grid_cell = f"{grid_x}_{grid_y}"

        if grid_cell not in spatial_index:
            spatial_index[grid_cell] = []

        spatial_index[grid_cell].append(building_id)

    return spatial_index


def create_material_groups(buildings_manifest: Dict[str, dict]) -> Dict[str, List[str]]:
    """
    Group buildings by material type for thermal property assignment.

    Args:
        buildings_manifest: Dictionary from export_buildings

    Returns:
        Dictionary mapping material types to lists of building IDs
    """
    material_groups = {
        'concrete': [],
        'brick': [],
        'wood': [],
        'metal': [],
        'unknown': []
    }

    for building_id, building_info in buildings_manifest.items():
        metadata = building_info.get('metadata', {})
        building_type = metadata.get('building_type', 'unknown')

        # Simple heuristic for material assignment
        # This could be enhanced with actual OSM building:material tags
        if building_type in ['commercial', 'industrial', 'office']:
            material_groups['concrete'].append(building_id)
        elif building_type in ['residential', 'house', 'apartments']:
            material_groups['brick'].append(building_id)
        elif building_type in ['shed', 'garage', 'warehouse']:
            material_groups['metal'].append(building_id)
        else:
            material_groups['unknown'].append(building_id)

    # Remove empty groups
    material_groups = {k: v for k, v in material_groups.items() if v}

    return material_groups


def save_material_mapping(
    material_groups: Dict[str, List[str]],
    output_path: str
):
    """
    Save material group mappings to a file.

    Args:
        material_groups: Dictionary from create_material_groups
        output_path: Output file path
    """
    mapping = {
        'description': 'Material group assignments for thermal property lookup',
        'groups': material_groups,
        'statistics': {
            material: len(buildings) for material, buildings in material_groups.items()
        }
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"Material mapping saved to {output_path}")


if __name__ == "__main__":
    # Test manifest creation
    test_manifest = {
        'building_1': {
            'filename': 'building_1.glb',
            'is_instance': False,
            'metadata': {
                'centroid_lat': 47.6062,
                'centroid_lon': -122.3321,
                'height': 30.0,
                'building_type': 'commercial',
                'area_sqm': 500.0
            }
        }
    }

    manifest = create_manifest(
        test_manifest,
        bounding_box=(47.61, 47.60, -122.33, -122.34),
        origin=(47.605, -122.335),
        output_path='test_manifest.json'
    )

    print(json.dumps(manifest, indent=2))
