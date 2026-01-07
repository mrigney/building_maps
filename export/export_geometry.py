"""
Export building geometries to various file formats (GLB, PLY)
"""
import trimesh
import numpy as np
import json
from pathlib import Path
from typing import List, Tuple, Dict
import os


def export_mesh_glb(mesh: trimesh.Trimesh, filepath: str, metadata: dict = None):
    """
    Export a mesh to GLB format.

    Args:
        mesh: Trimesh object to export
        filepath: Output file path
        metadata: Optional metadata to embed
    """
    # Add material groups if metadata contains building type
    if metadata and 'building_type' in metadata:
        # Create a simple material based on building type
        material = trimesh.visual.material.SimpleMaterial(
            ambient=(0.8, 0.8, 0.8),
            diffuse=(0.9, 0.9, 0.9)
        )
        mesh.visual = trimesh.visual.ColorVisuals(mesh=mesh)

    # Export to GLB
    mesh.export(filepath, file_type='glb')


def export_mesh_ply(mesh: trimesh.Trimesh, filepath: str):
    """
    Export a mesh to PLY format.

    Args:
        mesh: Trimesh object to export
        filepath: Output file path
    """
    mesh.export(filepath, file_type='ply')


def export_buildings(
    buildings: List[Tuple[str, trimesh.Trimesh, dict]],
    output_dir: str,
    format: str = 'glb'
) -> Dict[str, dict]:
    """
    Export all building meshes and return a manifest.

    Args:
        buildings: List of (building_id, mesh, metadata) tuples
        output_dir: Output directory for model files
        format: Export format ('glb' or 'ply')

    Returns:
        Dictionary mapping building_id to file info
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    manifest = {}

    print(f"Exporting {len(buildings)} buildings to {format.upper()} format...")

    for building_id, mesh, metadata in buildings:
        try:
            # Create filename
            filename = f"{building_id}.{format}"
            filepath = os.path.join(output_dir, filename)

            # Export based on format
            if format == 'glb':
                export_mesh_glb(mesh, filepath, metadata)
            elif format == 'ply':
                export_mesh_ply(mesh, filepath)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Add to manifest
            manifest[building_id] = {
                'filename': filename,
                'filepath': filepath,
                'format': format,
                'vertices': len(mesh.vertices),
                'faces': len(mesh.faces),
                'metadata': metadata
            }

        except Exception as e:
            print(f"Failed to export building {building_id}: {e}")
            continue

    print(f"Successfully exported {len(manifest)} buildings")

    return manifest


def export_combined_scene(
    buildings: List[Tuple[str, trimesh.Trimesh, dict]],
    filepath: str,
    format: str = 'glb'
):
    """
    Export all buildings as a single combined scene file.

    Args:
        buildings: List of (building_id, mesh, metadata) tuples
        filepath: Output file path
        format: Export format ('glb' or 'ply')
    """
    print(f"Creating combined scene with {len(buildings)} buildings...")

    # Combine all meshes
    meshes = [mesh for _, mesh, _ in buildings]

    if not meshes:
        print("No meshes to export")
        return

    combined_mesh = trimesh.util.concatenate(meshes)

    # Export
    if format == 'glb':
        export_mesh_glb(combined_mesh, filepath)
    elif format == 'ply':
        export_mesh_ply(combined_mesh, filepath)
    else:
        raise ValueError(f"Unsupported format: {format}")

    print(f"Combined scene exported to {filepath}")
    print(f"  Total vertices: {len(combined_mesh.vertices)}")
    print(f"  Total faces: {len(combined_mesh.faces)}")


def create_instanced_export(
    buildings: List[Tuple[str, trimesh.Trimesh, dict]],
    output_dir: str,
    format: str = 'glb',
    tolerance: float = 0.1
) -> Tuple[Dict[str, dict], Dict[str, List[str]]]:
    """
    Export buildings with instancing - similar buildings share the same mesh.

    Args:
        buildings: List of (building_id, mesh, metadata) tuples
        output_dir: Output directory for model files
        format: Export format
        tolerance: Relative tolerance for grouping similar buildings

    Returns:
        (manifest, instance_groups) where instance_groups maps prototype_id to list of building_ids
    """
    from ..utils.config import MIN_INSTANCES_FOR_SHARING

    print(f"Analyzing buildings for instancing (tolerance={tolerance})...")

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Group buildings by similar dimensions
    dimension_groups = {}

    for building_id, mesh, metadata in buildings:
        # Get bounding box dimensions
        bounds = mesh.bounds
        dims = bounds[1] - bounds[0]  # [dx, dy, dz]

        # Normalize dimensions for comparison
        dims_tuple = tuple(np.round(dims / tolerance) * tolerance)

        if dims_tuple not in dimension_groups:
            dimension_groups[dims_tuple] = []

        dimension_groups[dims_tuple].append((building_id, mesh, metadata))

    print(f"Found {len(dimension_groups)} unique building dimension groups")

    # Export prototypes and create manifest
    manifest = {}
    instance_groups = {}

    prototype_counter = 0

    for dims, group in dimension_groups.items():
        if len(group) >= MIN_INSTANCES_FOR_SHARING:
            # Create a prototype for this group
            prototype_id = f"prototype_{prototype_counter}"
            prototype_counter += 1

            # Use the first building as the prototype
            _, prototype_mesh, prototype_metadata = group[0]

            # Export prototype
            filename = f"{prototype_id}.{format}"
            filepath = os.path.join(output_dir, filename)

            if format == 'glb':
                export_mesh_glb(prototype_mesh, filepath, prototype_metadata)
            elif format == 'ply':
                export_mesh_ply(prototype_mesh, filepath)

            # Record all instances
            instance_groups[prototype_id] = []

            for building_id, mesh, metadata in group:
                manifest[building_id] = {
                    'prototype': prototype_id,
                    'filename': filename,
                    'filepath': filepath,
                    'is_instance': True,
                    'metadata': metadata
                }
                instance_groups[prototype_id].append(building_id)

            print(f"  Prototype {prototype_id}: {len(group)} instances (dims: {dims})")

        else:
            # Export individually
            for building_id, mesh, metadata in group:
                filename = f"{building_id}.{format}"
                filepath = os.path.join(output_dir, filename)

                if format == 'glb':
                    export_mesh_glb(mesh, filepath, metadata)
                elif format == 'ply':
                    export_mesh_ply(mesh, filepath)

                manifest[building_id] = {
                    'filename': filename,
                    'filepath': filepath,
                    'is_instance': False,
                    'metadata': metadata
                }

    unique_files = len([v for v in manifest.values() if 'prototype' not in v]) + prototype_counter
    print(f"Exported {unique_files} unique model files for {len(buildings)} buildings")

    return manifest, instance_groups


if __name__ == "__main__":
    # Test export
    from shapely.geometry import Polygon
    import sys
    sys.path.append('..')
    from geometry.extrude_buildings import extrude_polygon

    # Create test buildings
    test_buildings = []

    for i in range(3):
        footprint = Polygon([(i*30, 0), (i*30+10, 0), (i*30+10, 20), (i*30, 20)])
        mesh = extrude_polygon(footprint, height=30.0)
        metadata = {'building_id': f'test_{i}', 'height': 30.0, 'building_type': 'residential'}
        test_buildings.append((f'test_{i}', mesh, metadata))

    # Test export
    manifest = export_buildings(test_buildings, 'test_output', format='glb')
    print(f"Manifest: {json.dumps(manifest, indent=2)}")
