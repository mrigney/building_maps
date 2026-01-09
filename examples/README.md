# Example Output

This directory contains example output from the Urban Terrain Generator to help you understand what the tool produces.

## Available Examples

### Seattle Downtown
- **Location:** Small section of downtown Seattle, WA
- **Size:** ~200m x 200m
- **Buildings:** 21 buildings
- **Files:** Manifest, models, and visualizations

See [seattle_downtown/README.md](seattle_downtown/README.md) for details.

## What's Included in Each Example

Each example directory contains:

### Data Files
1. **`manifest.json`** - Complete building metadata
   - Building positions (lat/lon)
   - Height and area information
   - Building types
   - Model file references

2. **`material_mapping.json`** - Material grouping data
   - Groups buildings by similar characteristics
   - Useful for applying textures/materials in game engines

3. **`models/`** - Individual GLB files
   - One 3D model per building
   - Standard GLB format (compatible with most 3D tools)
   - Includes geometry and basic materials

### Visualization Files
1. **`building_map.html`** - Interactive 2D map
   - Open in any web browser
   - Click buildings for details
   - Pan and zoom
   - Color-coded by height

2. **`building_viewer_3d.html`** - Interactive 3D viewer
   - Open in any web browser
   - Navigate with mouse (rotate, pan, zoom)
   - Click buildings for information
   - See actual 3D geometry

3. **`building_visualization.png`** - Static overview image
   - Two-panel matplotlib visualization
   - Left: Buildings colored by height
   - Right: Buildings colored by type

## How to Use Examples

### View Visualizations
Simply open the HTML files in your web browser:
```bash
# Navigate to an example
cd examples/seattle_downtown

# Open 2D map (Linux/Mac)
open building_map.html

# Open 2D map (Windows)
start building_map.html

# Or double-click the files in your file explorer
```

### Import into 3D Software
The GLB files in the `models/` directory can be imported into:
- Blender
- Unity
- Unreal Engine
- Three.js
- Babylon.js
- And most other 3D tools

### Use as Test Data
Use the manifest.json to:
- Test your own visualization tools
- Understand the data structure
- Develop game engine integrations
- Create custom processing pipelines

## Generating Your Own Examples

To generate similar output for any location:

```bash
# Basic usage
python generate_urban_terrain.py \
  --bbox NORTH SOUTH EAST WEST \
  --format glb

# With verbose output
python generate_urban_terrain.py \
  --bbox 47.6080 47.6060 -122.3340 -122.3360 \
  --format glb \
  --verbose

# Then create visualizations
python tools/visualize_manifest.py output/manifest.json --all
```

See the main [README.md](../README.md) for more details.

## Data Attribution

All building data is sourced from [OpenStreetMap](https://www.openstreetmap.org/).

© OpenStreetMap contributors
Data available under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/)
