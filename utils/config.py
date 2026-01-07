"""
Configuration settings for urban terrain generator
"""

# Default building height if not available in data (meters)
DEFAULT_BUILDING_HEIGHT = 10.0

# Height per floor estimate (meters)
HEIGHT_PER_FLOOR = 3.0

# Coordinate reference system
CRS_WGS84 = "EPSG:4326"  # lat/lon
CRS_WEB_MERCATOR = "EPSG:3857"  # meters

# Export settings
EXPORT_FORMAT = "glb"  # "glb" or "ply"
GEOMETRY_PRECISION = 3  # decimal places for coordinates

# Instancing settings
DIMENSION_TOLERANCE = 0.1  # relative tolerance for grouping similar buildings
MIN_INSTANCES_FOR_SHARING = 3  # minimum instances to create shared model

# Output directories
OUTPUT_DIR = "output"
MODELS_DIR = "output/models"
MANIFEST_FILE = "output/manifest.json"
