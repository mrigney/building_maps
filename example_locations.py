"""
Example bounding boxes for testing the urban terrain generator

Run these examples with:
    python generate_urban_terrain.py --bbox {coordinates} --format glb --instancing
"""

EXAMPLE_LOCATIONS = {
    'downtown_seattle_small': {
        'description': 'Small downtown Seattle area (~0.25 km²)',
        'bbox': (47.6097, 47.6047, -122.3320, -122.3420),
        'command': 'py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing'
    },

    'times_square_nyc': {
        'description': 'Times Square, New York City (~0.25 km²)',
        'bbox': (40.7614, 40.7564, -73.9826, -73.9876),
        'command': 'py generate_urban_terrain.py --bbox 40.7614 40.7564 -73.9826 -73.9876 --format glb --instancing'
    },

    'downtown_boston': {
        'description': 'Downtown Boston area (~0.25 km²)',
        'bbox': (42.3601, 42.3551, -71.0552, -71.0602),
        'command': 'py generate_urban_terrain.py --bbox 42.3601 42.3551 -71.0552 -71.0602 --format glb --instancing'
    },

    'downtown_sf': {
        'description': 'Downtown San Francisco (~0.25 km²)',
        'bbox': (37.7899, 37.7849, -122.4012, -122.4062),
        'command': 'py generate_urban_terrain.py --bbox 37.7899 37.7849 -122.4012 -122.4062 --format glb --instancing'
    },

    'mit_campus': {
        'description': 'MIT Campus, Cambridge (~0.5 km²)',
        'bbox': (42.3625, 42.3575, -71.0875, -71.0925),
        'command': 'py generate_urban_terrain.py --bbox 42.3625 42.3575 -71.0875 -71.0925 --format glb --instancing'
    },

    'georgetown_dc': {
        'description': 'Georgetown, Washington DC (~0.5 km²)',
        'bbox': (38.9100, 38.9050, -77.0600, -77.0650),
        'command': 'py generate_urban_terrain.py --bbox 38.9100 38.9050 -77.0600 -77.0650 --format glb --instancing'
    }
}


def print_examples():
    """Print all example locations with commands"""
    print("=" * 80)
    print("EXAMPLE LOCATIONS FOR URBAN TERRAIN GENERATOR")
    print("=" * 80)
    print()

    for name, info in EXAMPLE_LOCATIONS.items():
        print(f"{name.replace('_', ' ').title()}")
        print(f"  Description: {info['description']}")
        print(f"  Bounding Box: {info['bbox']}")
        print(f"  Command:")
        print(f"    {info['command']}")
        print()


if __name__ == "__main__":
    print_examples()
