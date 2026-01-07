"""
Extrude building footprints into 3D geometries
"""
import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon
from typing import List, Tuple
import geopandas as gpd


def extrude_polygon(polygon: Polygon, height: float, base_elevation: float = 0.0) -> trimesh.Trimesh:
    """
    Extrude a 2D polygon to create a 3D building mesh.

    Args:
        polygon: 2D footprint polygon (in local meter coordinates)
        height: Building height in meters
        base_elevation: Base elevation (default 0.0)

    Returns:
        Trimesh object representing the extruded building
    """
    # Get exterior coordinates
    coords = np.array(polygon.exterior.coords[:-1])  # Remove duplicate last point

    num_points = len(coords)

    # Create vertices: bottom face + top face
    vertices_bottom = np.column_stack([coords, np.full(num_points, base_elevation)])
    vertices_top = np.column_stack([coords, np.full(num_points, base_elevation + height)])

    vertices = np.vstack([vertices_bottom, vertices_top])

    # Create faces
    faces = []

    # Bottom face (reverse winding for correct normal)
    bottom_face = list(range(num_points - 1, -1, -1))
    faces.append(bottom_face)

    # Top face
    top_face = list(range(num_points, 2 * num_points))
    faces.append(top_face)

    # Side faces (quads split into two triangles)
    for i in range(num_points):
        next_i = (i + 1) % num_points

        # Bottom-left, bottom-right, top-right
        face1 = [i, next_i, num_points + next_i]
        faces.append(face1)

        # Bottom-left, top-right, top-left
        face2 = [i, num_points + next_i, num_points + i]
        faces.append(face2)

    # Triangulate the top and bottom faces
    try:
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

        # Fix the polygon faces (top and bottom)
        # Use trimesh's built-in triangulation
        bottom_polygon = trimesh.path.polygons.polygons_enclosure_tree([coords])[0]
        top_coords = coords.copy()

        # Create separate meshes for top and bottom caps
        bottom_mesh = triangulate_polygon_face(coords, base_elevation, flip_normal=True)
        top_mesh = triangulate_polygon_face(coords, base_elevation + height, flip_normal=False)

        # Create side walls mesh
        side_vertices = []
        side_faces = []

        for i in range(num_points):
            next_i = (i + 1) % num_points

            v_idx = len(side_vertices)

            # Add 4 vertices for this wall segment
            side_vertices.extend([
                [coords[i][0], coords[i][1], base_elevation],
                [coords[next_i][0], coords[next_i][1], base_elevation],
                [coords[next_i][0], coords[next_i][1], base_elevation + height],
                [coords[i][0], coords[i][1], base_elevation + height]
            ])

            # Two triangles for this wall segment
            side_faces.extend([
                [v_idx, v_idx + 1, v_idx + 2],
                [v_idx, v_idx + 2, v_idx + 3]
            ])

        side_mesh = trimesh.Trimesh(vertices=side_vertices, faces=side_faces, process=False)

        # Combine all parts
        meshes = [m for m in [bottom_mesh, top_mesh, side_mesh] if m is not None]
        if meshes:
            combined_mesh = trimesh.util.concatenate(meshes)
            return combined_mesh
        else:
            return side_mesh

    except Exception as e:
        print(f"Warning: Failed to create proper mesh, using simple extrusion: {e}")
        # Fallback to simple box if triangulation fails
        return create_simple_box(coords, height, base_elevation)


def triangulate_polygon_face(coords: np.ndarray, z: float, flip_normal: bool = False) -> trimesh.Trimesh:
    """
    Create a triangulated face from 2D coordinates at a given z-height.

    Args:
        coords: 2D coordinates of polygon
        z: Z-height for the face
        flip_normal: Whether to flip the face normal

    Returns:
        Trimesh of the triangulated face
    """
    try:
        # Create vertices at specified z-height
        vertices_2d = coords
        vertices_3d = np.column_stack([vertices_2d, np.full(len(vertices_2d), z)])

        # Triangulate using earcut algorithm via trimesh
        polygon_2d = Polygon(coords)
        triangulation = trimesh.creation.triangulate_polygon(polygon_2d, engine='triangle')

        # Create 3D vertices
        faces = triangulation[1]

        if flip_normal:
            faces = faces[:, ::-1]  # Reverse winding order

        return trimesh.Trimesh(vertices=vertices_3d, faces=faces, process=False)

    except Exception as e:
        print(f"Triangulation failed: {e}")
        return None


def create_simple_box(coords: np.ndarray, height: float, base_elevation: float) -> trimesh.Trimesh:
    """
    Create a simple box from polygon bounds as fallback.

    Args:
        coords: Polygon coordinates
        height: Building height
        base_elevation: Base elevation

    Returns:
        Simple box mesh
    """
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)

    # Create box
    box = trimesh.creation.box(
        extents=[max_x - min_x, max_y - min_y, height],
        transform=trimesh.transformations.translation_matrix(
            [(min_x + max_x) / 2, (min_y + max_y) / 2, base_elevation + height / 2]
        )
    )

    return box


def extrude_buildings(buildings_gdf: gpd.GeoDataFrame, origin_lat: float, origin_lon: float) -> List[Tuple[str, trimesh.Trimesh, dict]]:
    """
    Extrude all buildings in a GeoDataFrame to 3D meshes.

    Args:
        buildings_gdf: GeoDataFrame with building footprints
        origin_lat: Origin latitude for coordinate transformation
        origin_lon: Origin longitude for coordinate transformation

    Returns:
        List of tuples: (building_id, mesh, metadata)
    """
    from ..utils.geo_utils import polygon_to_local_coords

    extruded_buildings = []

    print(f"Extruding {len(buildings_gdf)} buildings...")

    for idx, building in buildings_gdf.iterrows():
        try:
            # Get geometry and convert to local coordinates
            geom = building.geometry

            # Handle MultiPolygon by taking the largest polygon
            if isinstance(geom, MultiPolygon):
                geom = max(geom.geoms, key=lambda p: p.area)

            if not isinstance(geom, Polygon):
                continue

            # Convert to local meter coordinates
            local_polygon = polygon_to_local_coords(geom, origin_lat, origin_lon)

            # Get height
            height = building.get('height_m', 10.0)

            # Extrude
            mesh = extrude_polygon(local_polygon, height)

            # Collect metadata
            metadata = {
                'building_id': building.get('building_id', f'building_{idx}'),
                'height': height,
                'building_type': building.get('building', 'unknown'),
                'centroid_lat': geom.centroid.y,
                'centroid_lon': geom.centroid.x,
                'area_sqm': geom.area * 111320 * 111320 * np.cos(np.radians(geom.centroid.y))  # Approx
            }

            extruded_buildings.append((metadata['building_id'], mesh, metadata))

        except Exception as e:
            print(f"Failed to extrude building {idx}: {e}")
            continue

    print(f"Successfully extruded {len(extruded_buildings)} buildings")

    return extruded_buildings


if __name__ == "__main__":
    # Test extrusion
    from shapely.geometry import Polygon
    import matplotlib.pyplot as plt

    # Create a simple rectangular footprint
    footprint = Polygon([(0, 0), (10, 0), (10, 20), (0, 20)])

    mesh = extrude_polygon(footprint, height=30.0)

    print(f"Created mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces")
    print(f"Mesh is watertight: {mesh.is_watertight}")
    print(f"Mesh bounds: {mesh.bounds}")
