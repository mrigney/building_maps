#!/usr/bin/env python3
"""
Urban Terrain Generator - Main Script

Generate 3D urban terrain models from OpenStreetMap data.

Usage:
    python generate_urban_terrain.py --bbox NORTH SOUTH EAST WEST [--format glb|ply] [--instancing]

Example:
    python generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_acquisition.fetch_osm import fetch_buildings, fetch_roads, process_building_heights
from geometry.extrude_buildings import extrude_buildings
from export.export_geometry import export_buildings, export_combined_scene, create_instanced_export
from export.export_manifest import create_manifest, create_material_groups, save_material_mapping
from utils.geo_utils import get_bounding_box_center
from utils.config import OUTPUT_DIR, MODELS_DIR, MANIFEST_FILE


def main():
    parser = argparse.ArgumentParser(
        description='Generate 3D urban terrain from OpenStreetMap data',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--bbox',
        nargs=4,
        type=float,
        metavar=('NORTH', 'SOUTH', 'EAST', 'WEST'),
        required=True,
        help='Bounding box coordinates in decimal degrees (e.g., 47.6097 47.6047 -122.3320 -122.3420)'
    )

    parser.add_argument(
        '--format',
        choices=['glb', 'ply'],
        default='glb',
        help='Output format for 3D models (default: glb)'
    )

    parser.add_argument(
        '--instancing',
        action='store_true',
        help='Enable instancing to reduce file count for similar buildings'
    )

    parser.add_argument(
        '--combined',
        action='store_true',
        help='Also export a single combined scene file with all buildings'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=OUTPUT_DIR,
        help=f'Output directory (default: {OUTPUT_DIR})'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output with detailed progress information'
    )

    args = parser.parse_args()

    # Extract bounding box
    north, south, east, west = args.bbox

    print("=" * 80)
    print("URBAN TERRAIN GENERATOR")
    print("=" * 80)
    print(f"Bounding box: ({south:.6f}, {west:.6f}) to ({north:.6f}, {east:.6f})")
    print(f"Output format: {args.format.upper()}")
    print(f"Instancing: {'Enabled' if args.instancing else 'Disabled'}")
    print(f"Verbose: {'Enabled' if args.verbose else 'Disabled'}")
    print("=" * 80)
    print()

    # Step 1: Fetch building data
    print("[1/6] Fetching building data from OpenStreetMap...")
    if args.verbose:
        print("  -> Querying Overpass API...")
        print("  -> This may take 30-120 seconds depending on area size and network speed...")
    buildings_gdf = fetch_buildings(north, south, east, west, verbose=args.verbose)

    if len(buildings_gdf) == 0:
        print("ERROR: No buildings found in the specified area!")
        return 1

    # Process building heights
    buildings_gdf = process_building_heights(buildings_gdf)
    print()

    # Step 2: Fetch road data (optional for now)
    print("[2/6] Fetching road network from OpenStreetMap...")
    if args.verbose:
        print("  -> Querying road network...")
    roads_gdf = fetch_roads(north, south, east, west, verbose=args.verbose)
    print()

    # Step 3: Calculate origin for local coordinate system
    print("[3/6] Setting up local coordinate system...")
    origin_lat, origin_lon = get_bounding_box_center(north, south, east, west)
    print(f"Origin: ({origin_lat:.6f}, {origin_lon:.6f})")
    print()

    # Step 4: Extrude buildings to 3D
    print("[4/6] Extruding buildings to 3D geometries...")
    extruded_buildings = extrude_buildings(buildings_gdf, origin_lat, origin_lon)

    if len(extruded_buildings) == 0:
        print("ERROR: Failed to extrude any buildings!")
        return 1

    print()

    # Step 5: Export geometries
    print("[5/6] Exporting geometries...")
    models_dir = Path(args.output_dir) / "models"

    if args.instancing:
        buildings_manifest, instance_groups = create_instanced_export(
            extruded_buildings,
            str(models_dir),
            format=args.format
        )
        print(f"Instance groups: {len(instance_groups)}")
    else:
        buildings_manifest = export_buildings(
            extruded_buildings,
            str(models_dir),
            format=args.format
        )

    # Export combined scene if requested
    if args.combined:
        combined_path = Path(args.output_dir) / f"combined_scene.{args.format}"
        export_combined_scene(extruded_buildings, str(combined_path), format=args.format)

    print()

    # Step 6: Create manifest and material mappings
    print("[6/6] Generating manifest and material mappings...")

    manifest_path = Path(args.output_dir) / "manifest.json"
    manifest = create_manifest(
        buildings_manifest,
        roads_data=None,  # TODO: Process roads
        bounding_box=(north, south, east, west),
        origin=(origin_lat, origin_lon),
        output_path=str(manifest_path)
    )

    # Create material groups
    material_groups = create_material_groups(buildings_manifest)
    material_path = Path(args.output_dir) / "material_mapping.json"
    save_material_mapping(material_groups, str(material_path))

    print()
    print("=" * 80)
    print("GENERATION COMPLETE!")
    print("=" * 80)
    print(f"Total buildings: {len(buildings_manifest)}")
    print(f"Unique models: {manifest['statistics']['unique_models']}")
    print(f"Output directory: {args.output_dir}")
    print(f"  - Models: {models_dir}")
    print(f"  - Manifest: {manifest_path}")
    print(f"  - Material mapping: {material_path}")
    if args.combined:
        print(f"  - Combined scene: {combined_path}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
