# Getting Started with Urban Terrain Generator

## Installation

### Step 1: Install Python Dependencies

```bash
cd urban-terrain-generator
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
py test_installation.py
```

This will check that all required packages are installed and working correctly.

## Your First Terrain Generation

### Option 1: Use Example Locations

View pre-configured example locations:

```bash
py example_locations.py
```

Then copy and run one of the suggested commands, for example:

```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing
```

### Option 2: Choose Your Own Location

1. **Find your bounding box coordinates:**
   - Go to [bboxfinder.com](http://bboxfinder.com) or [OpenStreetMap Export](https://www.openstreetmap.org/export)
   - Navigate to your area of interest
   - Draw a box around the area you want
   - Copy the coordinates (they'll be in format: south, west, north, east)
   - Reorder them to: north, south, east, west

2. **Run the generator:**

```bash
py generate_urban_terrain.py --bbox NORTH SOUTH EAST WEST --format glb --instancing
```

## Understanding the Output

After running the generator, you'll find files in the `output/` directory:

```
output/
├── models/                 # Individual building models
│   ├── osm_123.glb
│   ├── osm_124.glb
│   └── ...
├── manifest.json          # Master file with all building locations and metadata
├── material_mapping.json  # Building material groups for thermal properties
└── combined_scene.glb     # Optional: all buildings in one file (if --combined used)
```

### Using the Manifest File

The `manifest.json` is your key to understanding the terrain:

```json
{
  "metadata": {
    "coordinate_system": {
      "type": "local_meters",
      "origin_lat": 47.6072,
      "origin_lon": -122.3370
    }
  },
  "buildings": {
    "osm_123": {
      "model_file": "osm_123.glb",
      "position": {
        "lat": 47.6075,
        "lon": -122.3365
      },
      "properties": {
        "height_m": 25.5,
        "building_type": "commercial",
        "area_sqm": 450.2
      }
    }
  }
}
```

### Using Material Mapping for Thermal Properties

The `material_mapping.json` groups buildings by material:

```json
{
  "groups": {
    "concrete": ["osm_123", "osm_456"],
    "brick": ["osm_789", "osm_012"],
    "metal": ["osm_345"]
  }
}
```

Use this to assign thermal properties in your simulation software:
- Read the material_mapping.json
- For each material group, apply appropriate thermal properties from your material database
- Map the properties to the corresponding building models

## Command Line Options

### Required
- `--bbox N S E W`: Bounding box in decimal degrees

### Optional
- `--format {glb|ply}`: Output format (default: glb)
  - GLB: Binary glTF, widely supported, good for visualization
  - PLY: Simpler format, smaller files, good for thermal analysis

- `--instancing`: Enable smart instancing
  - Groups similar buildings to reduce file count
  - Recommended for areas with many buildings

- `--combined`: Export a single combined scene file
  - Useful for quick visualization
  - All buildings in one file

- `--output-dir PATH`: Custom output directory (default: output)

## Examples

### Basic urban area (glTF format)
```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb
```

### Large area with instancing (recommended)
```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing
```

### For thermal analysis (PLY format)
```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format ply --instancing
```

### Quick visualization (combined scene)
```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --combined
```

## Tips for Success

### Start Small
- Begin with 0.25-0.5 km² areas
- Test with a small area before scaling up
- Urban areas: ~500m x 500m is a good starting size

### Area Size Guidelines
| Area Type | Recommended Size | Expected Buildings |
|-----------|------------------|-------------------|
| Single block | 100m x 100m | 5-20 |
| Small neighborhood | 500m x 500m | 50-200 |
| Urban district | 1km x 1km | 200-1000 |
| Large area | 2km x 2km | 1000+ |

### Performance Tips
- Use `--instancing` for areas with many buildings
- Use PLY format for large datasets (smaller file size)
- Start without `--combined` for large areas (it creates one huge file)

### Coordinate System Notes
- All models use a local meter-based coordinate system
- Origin is at the center of your bounding box
- +X = East, +Y = North, +Z = Up
- This makes it easy to integrate with most simulation software

## Troubleshooting

### "No buildings found"
- Your bounding box might be too small
- Try a larger area or different location
- Check coordinate order: NORTH SOUTH EAST WEST

### "Import Error" or "Module not found"
```bash
pip install -r requirements.txt
```

### Very slow downloads
- OpenStreetMap may rate-limit requests
- Try a smaller area
- Wait a few minutes between runs

### Out of memory
- Reduce the area size
- Use `--instancing` flag
- Use PLY format instead of GLB

## Next Steps

Once you have generated your terrain:

1. **Inspect the output:**
   - Open GLB files in a 3D viewer (Blender, online GLB viewers)
   - Read the manifest.json to understand the structure

2. **Integrate with your heat equation solver:**
   - Parse the manifest.json to get building locations
   - Load the geometry files (GLB or PLY)
   - Apply thermal properties using material_mapping.json

3. **Iterate and refine:**
   - Adjust area size based on your needs
   - Experiment with instancing to optimize file count
   - Test with different locations

## Support and Documentation

- Full documentation: See [README.md](README.md)
- Example locations: Run `py example_locations.py`
- Test installation: Run `py test_installation.py`

## What's Next?

This is a basic prototype. Future enhancements will include:
- Road network 3D geometry
- Building facade details (windows, doors, roofs)
- Google Open Buildings integration
- Vegetation placement
- Custom material property configuration
