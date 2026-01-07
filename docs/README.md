# Urban Terrain Generator - Documentation

Welcome to the Urban Terrain Generator documentation! This tool generates 3D urban terrain models from OpenStreetMap data for thermal analysis and simulation.

## 📚 Documentation Structure

### 🚀 Getting Started
Perfect for first-time users and quick setup.

- **[READ THIS FIRST](getting-started/READ_THIS_FIRST.md)** - Start here! Current status and quick wins
- **[Getting Started Guide](getting-started/GETTING_STARTED.md)** - Installation and first terrain generation
- **[Quick Reference](#quick-reference)** - Common commands at a glance

### 📖 User Guides
Detailed guides for using the tool effectively.

- **[Workflow Guide](guides/WORKFLOW_GUIDE.md)** - Complete workflow from data to 3D models
- **[Verbose Mode Examples](guides/VERBOSE_EXAMPLE.md)** - Using --verbose for detailed progress

### 🔧 Troubleshooting
Solutions for common issues.

- **[OSM API Workarounds](troubleshooting/OSM_API_WORKAROUND.md)** - Alternative data sources when API is down
- **[Investigation Findings](troubleshooting/INVESTIGATION_FINDINGS.md)** - Technical details on known issues

### 📚 Reference
Technical documentation and architecture details.

- **[Project Summary](reference/PROJECT_SUMMARY.md)** - Architecture and technical overview
- **[GitHub Setup](reference/PUSH_TO_GITHUB.md)** - Repository management

---

## Quick Reference

### Installation
```bash
pip install -r requirements.txt
py test_installation.py
```

### Generate Terrain (Live Data)
```bash
py generate_urban_terrain.py --bbox NORTH SOUTH EAST WEST --format glb --instancing
```

### Generate Demo (No Network)
```bash
py create_demo_output.py
```

### Common Options
- `--format {glb|ply}` - Output format
- `--instancing` - Reduce file count for similar buildings
- `--combined` - Export single scene file
- `--verbose` - Show detailed progress
- `--output-dir DIR` - Custom output location

---

## For New Users

### I want to...

**...get started quickly**
→ [Getting Started Guide](getting-started/GETTING_STARTED.md)

**...understand the complete workflow**
→ [Workflow Guide](guides/WORKFLOW_GUIDE.md)

**...test without downloading data**
→ Run `py create_demo_output.py`

**...understand the output format**
→ Check `demo_output/README.md` after running demo

**...fix OSM API issues**
→ [OSM API Workarounds](troubleshooting/OSM_API_WORKAROUND.md)

**...understand the architecture**
→ [Project Summary](reference/PROJECT_SUMMARY.md)

**...integrate with my thermal solver**
→ [Workflow Guide - Using the Output](guides/WORKFLOW_GUIDE.md#using-the-output-in-your-heat-transfer-solver)

---

## Documentation by Experience Level

### Beginner
1. [READ THIS FIRST](getting-started/READ_THIS_FIRST.md)
2. [Getting Started Guide](getting-started/GETTING_STARTED.md)
3. Run the demo: `py create_demo_output.py`

### Intermediate
1. [Workflow Guide](guides/WORKFLOW_GUIDE.md)
2. [Verbose Mode](guides/VERBOSE_EXAMPLE.md)
3. Generate real data with `--bbox`

### Advanced
1. [Project Summary](reference/PROJECT_SUMMARY.md)
2. [Investigation Findings](troubleshooting/INVESTIGATION_FINDINGS.md)
3. Customize `utils/config.py`

---

## Key Concepts

### Bounding Box
Geographic coordinates defining your area of interest:
- **Format**: `NORTH SOUTH EAST WEST` (decimal degrees)
- **Example**: `47.6097 47.6047 -122.3320 -122.3420`
- **Size**: Start with 0.25-0.5 km² for testing

### Coordinate System
- **Input**: WGS84 lat/lon (degrees)
- **Output**: Local Cartesian (meters)
- **Origin**: Center of bounding box
- **Axes**: +X=East, +Y=North, +Z=Up

### Instancing
Optimization that reuses similar building models:
- Reduces file count by 60-80%
- Groups buildings by dimensions
- Maintains individual metadata

### Output Files
- **models/** - Individual building GLB/PLY files
- **manifest.json** - Master index with locations and metadata
- **material_mapping.json** - Material groups for thermal properties

---

## Example Workflows

### Quick Test
```bash
# 1. Install and verify
pip install -r requirements.txt
py test_installation.py

# 2. Generate demo data (instant)
py create_demo_output.py

# 3. Check output
ls demo_output/models/
```

### Real Data Generation
```bash
# 1. Find coordinates at bboxfinder.com

# 2. Generate with verbose output
py generate_urban_terrain.py \
  --bbox 47.6097 47.6047 -122.3320 -122.3420 \
  --format glb \
  --instancing \
  --verbose

# 3. Check results
cat output/manifest.json
```

### Thermal Analysis Pipeline
```bash
# 1. Generate terrain
py generate_urban_terrain.py --bbox ... --format ply --instancing

# 2. Review material mapping
cat output/material_mapping.json

# 3. Load in your solver (Python example)
python your_thermal_solver.py --manifest output/manifest.json
```

---

## Getting Help

### Check the Docs
1. Browse this documentation
2. Look for similar issues in troubleshooting
3. Check the demo output for expected format

### Common Issues
- **OSM API hangs**: See [OSM API Workarounds](troubleshooting/OSM_API_WORKAROUND.md)
- **No buildings found**: Try larger area or check coordinates
- **Import errors**: Run `py test_installation.py`

### Report Issues
- GitHub: https://github.com/mrigney/building_maps
- Include: Error message, command used, area size

---

## What's Next?

After getting familiar with the basics:

1. **Experiment with settings** - Try different formats and options
2. **Scale up** - Increase area size gradually
3. **Integrate** - Connect to your thermal solver
4. **Contribute** - Share improvements or report issues

---

## Documentation Updates

This documentation is maintained in the `docs/` folder. Each guide is self-contained but cross-referenced for easy navigation.

**Last Updated**: 2026-01-07
**Version**: v0.1
