# Urban Terrain Generator

A Python toolkit for generating 3D urban terrain models from open geographic data sources (OpenStreetMap and Google Open Buildings) for thermal analysis and simulation.

[![GitHub](https://img.shields.io/badge/GitHub-building__maps-blue?logo=github)](https://github.com/mrigney/building_maps)

## 📚 Documentation

**New users start here**: [Complete Documentation →](docs/)

- [Getting Started Guide](docs/getting-started/GETTING_STARTED.md)
- [Workflow Guide](docs/guides/WORKFLOW_GUIDE.md)
- [Troubleshooting](docs/troubleshooting/)
- [Reference Documentation](docs/reference/)

## Features

- **Automated Data Acquisition**: Fetch building footprints and road networks from OpenStreetMap
- **3D Geometry Generation**: Extrude 2D building footprints into 3D models with realistic heights
- **Multiple Export Formats**: Support for GLB and PLY file formats
- **Instancing Support**: Automatically group similar buildings to reduce file count
- **Material Grouping**: Organize buildings by material type for thermal property assignment
- **Spatial Manifest**: Generate comprehensive metadata and spatial indexing

## Quick Install

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

Generate urban terrain for a bounding box (e.g., downtown Seattle area):

```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing
```

### Command Line Arguments

- `--bbox NORTH SOUTH EAST WEST`: Bounding box coordinates in decimal degrees (required)
- `--format {glb|ply}`: Output format for 3D models (default: glb)
- `--instancing`: Enable instancing to reduce file count for similar buildings
- `--combined`: Also export a single combined scene file with all buildings
- `--output-dir DIR`: Output directory (default: output)
- `--verbose`: Enable detailed progress output during OSM data fetching

### Finding Coordinates

To get bounding box coordinates for your area of interest:

1. Go to [OpenStreetMap](https://www.openstreetmap.org)
2. Navigate to your desired location
3. Click "Export" in the top menu
4. The bounding box coordinates will be shown (or manually select an area)
5. Use format: `--bbox NORTH SOUTH EAST WEST`

## Output Files

The tool generates the following outputs in the specified output directory:

```
output/
├── models/                    # 3D model files (.glb or .ply)
│   ├── osm_12345.glb
│   ├── osm_12346.glb
│   └── ...
├── manifest.json              # Comprehensive manifest with all metadata
├── material_mapping.json      # Material group assignments
└── combined_scene.glb         # Optional combined scene (if --combined flag used)
```

### Manifest File

The `manifest.json` contains:

- **Metadata**: Generation timestamp, coordinate system, bounding box
- **Statistics**: Building counts, unique models
- **Buildings**: Each building with:
  - Model file reference
  - Geographic position (lat/lon)
  - Properties (height, type, area)
  - Instance information (if using instancing)

### Material Mapping

The `material_mapping.json` groups buildings by material type (concrete, brick, metal, wood) for thermal property assignment in your simulation software.

## Project Structure

```
urban-terrain-generator/
├── data_acquisition/          # Data fetching from OSM and Open Buildings
│   └── fetch_osm.py
├── geometry/                  # 3D geometry generation
│   └── extrude_buildings.py
├── export/                    # Export to various formats
│   ├── export_geometry.py
│   └── export_manifest.py
├── utils/                     # Utility functions
│   ├── config.py
│   └── geo_utils.py
├── generate_urban_terrain.py  # Main script
└── requirements.txt
```

## Examples

### Small Urban Area (0.5 km²)

```bash
# Downtown area with instancing enabled
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing --combined
```

### Custom Output Directory

```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format ply --output-dir my_custom_output
```

## Coordinate System

The tool uses a local meter-based coordinate system:

- **Origin**: Center of the bounding box
- **+X axis**: East
- **+Y axis**: North
- **+Z axis**: Up (height)

This makes it easy to integrate with thermal simulation software that expects Cartesian coordinates.

## Configuration

Edit `utils/config.py` to customize:

- Default building height (when no data available)
- Height per floor estimate
- Dimension tolerance for instancing
- Export precision
- Output paths

## Limitations and Future Work

### Current Limitations

- Road networks fetched but not yet converted to 3D geometry
- Google Open Buildings integration not yet implemented (currently OSM only)
- Building facades are simple extruded boxes (no windows/doors yet)
- Material assignment uses simple heuristics

### Planned Features

- Road network 3D geometry generation
- Google Open Buildings data source integration
- Procedural facade detail generation (windows, doors, roofs)
- Enhanced material detection from OSM tags
- Vegetation/tree placement
- Terrain elevation integration

## Need Help?

### Common Issues
- **OSM API hangs or fails**: See [OSM API Workarounds](docs/troubleshooting/OSM_API_WORKAROUND.md)
- **No buildings found**: Check coordinates and try a larger area
- **Import errors**: Run `py test_installation.py` to verify setup

### Full Documentation
📖 **[Browse Complete Documentation](docs/)** - Guides, tutorials, and troubleshooting

### Quick Links
- [Getting Started](docs/getting-started/GETTING_STARTED.md)
- [Complete Workflow](docs/guides/WORKFLOW_GUIDE.md)
- [Troubleshooting Guide](docs/troubleshooting/)
- [Architecture & Design](docs/reference/PROJECT_SUMMARY.md)

## Contributing

This is an initial prototype. Contributions and suggestions are welcome!

## License

This project uses open data from OpenStreetMap (ODbL license).
