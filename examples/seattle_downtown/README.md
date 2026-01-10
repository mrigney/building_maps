# Example Output: Seattle Downtown

This directory contains example output from the Urban Terrain Generator for a small section of downtown Seattle.

## Area Details

- **Location:** Seattle, Washington, USA
- **Bounding Box:**
  - North: 47.6080°
  - South: 47.6060°
  - East: -122.3340°
  - West: -122.3360°
- **Size:** Approximately 200m x 200m
- **Buildings:** 21 buildings
- **Roads:** 90 road segments
- **Generated:** 2026-01-09

## Files Included

### Data Files
- **`manifest.json`** - Building and road metadata with positions
- **`material_mapping.json`** - Material groupings for buildings
- **`models/`** - Directory containing 21 GLB 3D model files

### Visualization Files
- **`building_map.html`** - Interactive 2D map with roads (open in browser)
- **`building_viewer_3d.html`** - Interactive 3D viewer with roads (open in browser)
- **`building_visualization.png`** - Static matplotlib visualization with roads

## How to View

### Quick View
Open these files in your web browser:
- `building_map.html` - See buildings and roads on a 2D map
- `building_viewer_3d.html` - Explore buildings and roads in 3D

### Statistics

**Buildings:**
- **Total Buildings:** 21
- **Height Range:** 6.0m - 138.0m
- **Mean Height:** 27.2m
- **Building Types:** hotel, office, garage, commercial, service, residential

**Roads:**
- **Total Road Segments:** 90
- **Road Types:** footway (66), tertiary (9), service (4), secondary (4), primary (3)
- **Named Roads:** 18

### Notable Features
- **Tallest Building:** osm_232080287 (138.0m) - Appears to be a high-rise
- **Largest Building:** osm_35824976 (4,686 m²) - Hotel
- **Most Common Road Type:** Footway/pedestrian paths (73% of segments)

## Generation Command

This example was generated using:
```bash
python generate_urban_terrain.py \
  --bbox 47.6080 47.6060 -122.3340 -122.3360 \
  --format glb \
  --verbose
```

## Data Source

Building and road data sourced from [OpenStreetMap](https://www.openstreetmap.org/) via the Overpass API.

© OpenStreetMap contributors - Data available under the Open Database License (ODbL)
