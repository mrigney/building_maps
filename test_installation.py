#!/usr/bin/env python3
"""
Test script to verify installation and basic functionality
"""

import sys


def test_imports():
    """Test that all required packages can be imported"""
    print("Testing package imports...")

    required_packages = [
        ('geopandas', 'geopandas'),
        ('shapely', 'shapely'),
        ('osmnx', 'osmnx'),
        ('trimesh', 'trimesh'),
        ('numpy', 'numpy'),
        ('rtree', 'rtree'),
        ('requests', 'requests'),
    ]

    optional_packages = [
        ('pygltflib', 'pygltflib'),
        ('plyfile', 'plyfile'),
    ]

    failed = []

    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ✗ {display_name} - {e}")
            failed.append(display_name)

    print("\nOptional packages:")
    for display_name, import_name in optional_packages:
        try:
            __import__(import_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ⚠ {display_name} - {e} (optional)")

    if failed:
        print(f"\n❌ Missing required packages: {', '.join(failed)}")
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
        return False

    print("\n✅ All required packages installed!")
    return True


def test_basic_functionality():
    """Test basic geometry operations"""
    print("\nTesting basic functionality...")

    try:
        from shapely.geometry import Polygon
        import numpy as np

        # Test polygon creation
        polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        print(f"  ✓ Polygon creation (area: {polygon.area})")

        # Test coordinate transformation
        from utils.geo_utils import lat_lon_to_meters

        x, y = lat_lon_to_meters(47.6062, -122.3321, 47.6000, -122.3300)
        print(f"  ✓ Coordinate transformation ({x:.2f}m, {y:.2f}m)")

        print("\n✅ Basic functionality working!")
        return True

    except Exception as e:
        print(f"\n❌ Functionality test failed: {e}")
        return False


def test_osm_connection():
    """Test connection to OpenStreetMap"""
    print("\nTesting OpenStreetMap connection...")

    try:
        import osmnx as ox

        # Try to fetch a very small area (single building if possible)
        print("  Attempting to fetch data from OSM...")

        # Small test area in Seattle
        test_bbox = (47.6062, 47.6060, -122.3321, -122.3323)

        buildings = ox.features_from_bbox(
            north=test_bbox[0],
            south=test_bbox[1],
            east=test_bbox[2],
            west=test_bbox[3],
            tags={'building': True}
        )

        print(f"  ✓ OSM connection successful (found {len(buildings)} features)")
        print("\n✅ OpenStreetMap connection working!")
        return True

    except Exception as e:
        print(f"\n⚠ OSM connection test failed: {e}")
        print("This might be due to network issues or rate limiting.")
        print("The tool should still work when you run it with proper network access.")
        return False


def main():
    print("=" * 80)
    print("URBAN TERRAIN GENERATOR - INSTALLATION TEST")
    print("=" * 80)
    print()

    results = []

    # Test imports
    results.append(test_imports())

    # Test basic functionality
    if results[0]:
        results.append(test_basic_functionality())

    # Test OSM connection (optional)
    if results[0]:
        test_osm_connection()  # Don't fail overall test if this fails

    print()
    print("=" * 80)

    if all(results):
        print("✅ ALL TESTS PASSED!")
        print()
        print("You're ready to generate urban terrain!")
        print()
        print("Try running:")
        print("  python example_locations.py")
        print()
        print("Or generate terrain for a location:")
        print("  python generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please install missing dependencies:")
        print("  pip install -r requirements.txt")

    print("=" * 80)

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
