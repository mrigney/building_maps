# Reference Documentation

Technical documentation, architecture details, and advanced topics.

## Technical Documentation

### 🏗️ [Project Summary](PROJECT_SUMMARY.md)
**Complete architecture and technical overview**

Detailed information about:
- System architecture and data flow
- Module organization and responsibilities
- File formats and specifications
- Instancing algorithm
- Performance characteristics
- Integration points for thermal solvers

**Best for**: Understanding the system design and extending the codebase

---

### 📱 [GitHub Setup](PUSH_TO_GITHUB.md)
**Repository management and GitHub integration**

Instructions for:
- Creating GitHub repository
- Pushing code to GitHub
- Repository configuration
- Topics and metadata

**Best for**: Setting up your own fork or contributing

---

## Key Concepts Reference

### Coordinate Systems

**Input (WGS84)**:
- Latitude/Longitude in decimal degrees
- Example: 47.6072°N, 122.3370°W

**Output (Local Cartesian)**:
- Origin: Center of bounding box
- Units: Meters
- Axes: +X=East, +Y=North, +Z=Up

### File Formats

**GLB (Binary glTF 2.0)**:
- Widely supported 3D format
- Good for visualization
- Can include materials and textures
- ~5-50 KB per building

**PLY (Stanford Polygon Format)**:
- Simpler geometry-only format
- More compact (~2-20 KB per building)
- Fast to parse
- Ideal for computational analysis

### Output Structure

```
output/
├── models/              # Individual building files
│   ├── osm_123.glb
│   └── ...
├── manifest.json        # Master index with metadata
└── material_mapping.json  # Material groups
```

### Manifest Schema

```json
{
  "metadata": {
    "generated": "ISO timestamp",
    "coordinate_system": {
      "type": "local_meters",
      "origin_lat": float,
      "origin_lon": float
    },
    "bounding_box": {...}
  },
  "statistics": {...},
  "buildings": {
    "building_id": {
      "model_file": "filename.glb",
      "position": {"lat": float, "lon": float},
      "properties": {...}
    }
  }
}
```

---

## Module Reference

### Data Acquisition (`data_acquisition/`)
- `fetch_osm.py` - OpenStreetMap data fetching
- `fetch_from_geojson.py` - Local GeoJSON import

### Geometry (`geometry/`)
- `extrude_buildings.py` - 3D extrusion algorithms

### Export (`export/`)
- `export_geometry.py` - GLB/PLY export with instancing
- `export_manifest.py` - Metadata generation

### Utils (`utils/`)
- `config.py` - Configuration settings
- `geo_utils.py` - Geographic transformations

---

## Configuration Reference

Edit `utils/config.py` to customize:

```python
# Default building height (meters)
DEFAULT_BUILDING_HEIGHT = 10.0

# Height per floor estimate (meters)
HEIGHT_PER_FLOOR = 3.0

# Export format
EXPORT_FORMAT = "glb"  # or "ply"

# Instancing settings
DIMENSION_TOLERANCE = 0.1  # Relative tolerance
MIN_INSTANCES_FOR_SHARING = 3  # Minimum reuse count
```

---

## Performance Characteristics

### Processing Times (Typical)
- 100 buildings: ~10-30 seconds
- 500 buildings: ~1-2 minutes
- 1000 buildings: ~2-5 minutes

*Times vary based on complexity and network speed*

### File Sizes
- **GLB**: ~5-50 KB per building
- **PLY**: ~2-20 KB per building
- **With instancing**: 60-80% reduction

### Memory Usage
- ~1-5 MB per 100 buildings
- Scales linearly with building count

---

## API Reference

### Command Line Interface

```bash
py generate_urban_terrain.py [OPTIONS]
```

**Options**:
- `--bbox N S E W` - Bounding box (required)
- `--format {glb|ply}` - Output format
- `--instancing` - Enable instancing
- `--combined` - Export combined scene
- `--output-dir DIR` - Output directory
- `--verbose` - Detailed progress

### Python API

```python
from data_acquisition.fetch_osm import fetch_buildings
from geometry.extrude_buildings import extrude_buildings
from export.export_geometry import export_buildings

# Fetch data
buildings = fetch_buildings(north, south, east, west)

# Extrude to 3D
extruded = extrude_buildings(buildings, origin_lat, origin_lon)

# Export
manifest = export_buildings(extruded, output_dir, format='glb')
```

---

## Advanced Topics

### Custom Material Properties

Extend `create_material_groups()` to add your own material classification:

```python
def custom_material_classifier(building_metadata):
    # Your custom logic
    if building_metadata['building_type'] == 'factory':
        return 'industrial_metal'
    return 'default'
```

### Custom Export Formats

Implement new exporters by following the pattern in `export_geometry.py`:

```python
def export_mesh_custom(mesh: trimesh.Trimesh, filepath: str):
    # Your export logic
    pass
```

### Integration with Other Tools

The manifest.json format is designed for easy integration:
- JSON parsing in any language
- Clear coordinate system definition
- Standard file format references

---

## Related Documentation

- **Getting Started** → [Installation & First Steps](../getting-started/)
- **User Guides** → [Workflows & Examples](../guides/)
- **Troubleshooting** → [Common Issues](../troubleshooting/)

---

[← Back to Documentation Home](../)
