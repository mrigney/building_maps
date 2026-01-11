# Phase 1: Quick Start Guide

## Generate Urban Terrain with Enhanced Road Data

### Basic Command
```bash
py generate_urban_terrain.py --bbox 47.608 47.606 -122.334 -122.336 --format glb
```

### What You'll Get

**New Output Files:**
- `output/manifest.json` - Now includes road width and surface material data
- `output/road_material_mapping.json` - **NEW!** Thermal properties for road materials

### View Your Results

**Open the HTML map:**
```bash
py tools/create_simple_html_map.py output/manifest.json -o output/map.html
start output/map.html
```

Roads will now show:
- ✅ Realistic widths based on road type and OSM data
- ✅ Colors based on surface material (asphalt=dark, concrete=light, etc.)
- ✅ Click roads to see width and surface material

## Access Road Data in Python

```python
import json

# Load manifest
with open('output/manifest.json') as f:
    data = json.load(f)

# Access a road
road = data['roads']['osm_road_123']

# Get road properties
print(f"Width: {road['properties']['width_m']}m")
print(f"Material: {road['properties']['surface_material']}")
print(f"Polygon vertices: {len(road.get('surface_polygon_local_m', []))} points")

# Load thermal properties
with open('output/road_material_mapping.json') as f:
    materials = json.load(f)

# Get thermal properties for asphalt
asphalt = materials['thermal_properties_reference']['materials']['asphalt_road']
print(f"Thermal conductivity: {asphalt['thermal_conductivity']} W/(m·K)")
print(f"Emissivity: {asphalt['emissivity']}")
```

## Road Material Types

| Material | Typical Surfaces | Thermal Conductivity |
|----------|------------------|---------------------|
| `asphalt_road` | Motorways, primary roads | 0.75 W/(m·K) |
| `concrete_road` | Major streets, highways | 1.4 W/(m·K) |
| `concrete_walkway` | Sidewalks, pedestrian areas | 1.4 W/(m·K) |
| `brick_paved` | Historic areas, plazas | 0.72 W/(m·K) |
| `gravel` | Service roads, paths | 0.52 W/(m·K) |
| `dirt` | Unpaved roads | 0.25 W/(m·K) |

## Road Width Calculation

The system automatically calculates width from:
1. Explicit OSM `width` tag (if available)
2. Number of lanes × 3.5m
3. Default for road type:
   - Motorway: 12m
   - Primary: 8m
   - Secondary: 7m
   - Residential: 5.5m
   - Footway: 2m

## For Your Thermal Solver

**Road Surface Polygon:**
```python
# Get polygon vertices in local meter coordinates
polygon = road['surface_polygon_local_m']  # List of [x, y] tuples
# polygon = [[0.0, 0.0], [0.0, 100.0], [8.0, 100.0], [8.0, 0.0]]

# Use these vertices to create thermal mesh elements
```

**Material Properties:**
```python
material_name = road['properties']['surface_material']  # e.g., "asphalt_road"

# Look up thermal properties
props = materials['thermal_properties_reference']['materials'][material_name]

# Apply to thermal solver:
# - Thermal conductivity: props['thermal_conductivity']
# - Emissivity: props['emissivity']
# - Solar absorptivity: props['solar_absorptivity']
# - Density: props['density']
# - Specific heat: props['specific_heat']
```

## Next: Phase 2

Once you've validated Phase 1 works for your needs, we can move to:
- Phase 2: Building footprint validation
- Phase 3: Procedural facade details
- Phase 4: Google Open Buildings integration

---

**Questions?** See [PHASE1_IMPLEMENTATION_SUMMARY.md](PHASE1_IMPLEMENTATION_SUMMARY.md) for complete details.
