#!/usr/bin/env python3
"""
Create demo output without fetching from OSM - for testing/demonstration
"""

import sys
import json
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon
import trimesh

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from geometry.extrude_buildings import extrude_polygon
from export.export_geometry import export_mesh_glb, export_mesh_ply
from export.export_manifest import create_manifest, create_material_groups, save_material_mapping


def create_demo_buildings():
    """Create some synthetic building data for demonstration"""

    print("Creating demo building data...")

    buildings = []

    # Create a grid of buildings
    for i in range(5):
        for j in range(5):
            # Random building dimensions
            width = np.random.uniform(15, 30)
            length = np.random.uniform(20, 40)
            height = np.random.uniform(10, 50)

            # Position
            x = i * 50
            y = j * 50

            # Create footprint
            footprint = Polygon([
                (x, y),
                (x + width, y),
                (x + width, y + length),
                (x, y + length)
            ])

            # Extrude to 3D
            mesh = extrude_polygon(footprint, height)

            # Create metadata
            building_types = ['residential', 'commercial', 'commercial', 'industrial', 'residential']
            building_type = building_types[i % len(building_types)]

            # Calculate centroid in fake lat/lon
            centroid_lat = 40.7580 + (y / 111320)  # Approx meters to degrees
            centroid_lon = -73.9689 + (x / (111320 * np.cos(np.radians(40.7580))))

            metadata = {
                'building_id': f'demo_{i}_{j}',
                'height': height,
                'building_type': building_type,
                'centroid_lat': centroid_lat,
                'centroid_lon': centroid_lon,
                'area_sqm': width * length
            }

            buildings.append((metadata['building_id'], mesh, metadata))

    print(f"Created {len(buildings)} demo buildings")
    return buildings


def main():
    output_dir = Path("demo_output")
    models_dir = output_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("URBAN TERRAIN GENERATOR - DEMO OUTPUT CREATOR")
    print("=" * 80)
    print()

    # Create demo buildings
    buildings = create_demo_buildings()
    print()

    # Export to GLB
    print("Exporting buildings to GLB format...")
    buildings_manifest = {}

    for building_id, mesh, metadata in buildings:
        filename = f"{building_id}.glb"
        filepath = models_dir / filename

        export_mesh_glb(mesh, str(filepath), metadata)

        buildings_manifest[building_id] = {
            'filename': filename,
            'filepath': str(filepath),
            'is_instance': False,
            'metadata': metadata
        }

    print(f"Exported {len(buildings_manifest)} buildings")
    print()

    # Create manifest
    print("Creating manifest...")
    manifest_path = output_dir / "manifest.json"
    manifest = create_manifest(
        buildings_manifest,
        bounding_box=(40.7584, 40.7576, -73.9685, -73.9693),
        origin=(40.7580, -73.9689),
        output_path=str(manifest_path)
    )
    print()

    # Create material mapping
    print("Creating material mapping...")
    material_groups = create_material_groups(buildings_manifest)
    material_path = output_dir / "material_mapping.json"
    save_material_mapping(material_groups, str(material_path))
    print()

    # Export a combined scene
    print("Creating combined scene...")
    meshes = [mesh for _, mesh, _ in buildings]
    combined_mesh = trimesh.util.concatenate(meshes)
    combined_path = output_dir / "combined_scene.glb"
    export_mesh_glb(combined_mesh, str(combined_path))
    print(f"Combined scene saved to {combined_path}")
    print()

    print("=" * 80)
    print("DEMO OUTPUT COMPLETE!")
    print("=" * 80)
    print(f"Output directory: {output_dir.absolute()}")
    print(f"  - {len(buildings_manifest)} building models in models/")
    print(f"  - manifest.json")
    print(f"  - material_mapping.json")
    print(f"  - combined_scene.glb")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
