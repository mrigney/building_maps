# Visualization Tools

This directory contains tools for visualizing the output from the Urban Terrain Generator.

## Available Tools

### 1. visualize_manifest.py
Multi-format visualization tool with several output options.

**Usage:**
```bash
# ASCII terminal view (no dependencies)
python tools/visualize_manifest.py output/manifest.json --ascii

# Matplotlib plot (requires matplotlib)
python tools/visualize_manifest.py output/manifest.json --plot --output viz.png

# Interactive HTML map (requires folium)
python tools/visualize_manifest.py output/manifest.json --html map.html

# Generate all formats
python tools/visualize_manifest.py output/manifest.json --all
```

**Features:**
- ASCII art visualization in terminal
- Static matplotlib plots (2 panels: height and type)
- Interactive Folium HTML maps
- Batch processing support

**Dependencies:**
- ASCII mode: None (built-in Python)
- Plot mode: `matplotlib`
- HTML mode: `folium`

---

### 2. create_simple_html_map.py
Creates a lightweight interactive 2D map using Leaflet.js.

**Usage:**
```bash
python tools/create_simple_html_map.py output/manifest.json -o map.html
```

**Features:**
- Zero Python dependencies (uses Leaflet.js CDN)
- Self-contained HTML file
- Interactive pan/zoom
- Click buildings for details
- Color-coded by height
- Statistics panel

**Best for:** Quick sharing and simple visualization

---

### 3. create_3d_viewer.py
Creates an interactive 3D viewer using Three.js.

**Usage:**
```bash
python tools/create_3d_viewer.py output/manifest.json -o viewer_3d.html
```

**Features:**
- Zero Python dependencies (uses Three.js CDN)
- Self-contained HTML file
- Loads actual GLB models
- Orbit camera controls
- Click buildings for information
- Real-time lighting and shadows
- Ground plane and grid

**Controls:**
- Left mouse: Rotate
- Right mouse: Pan
- Scroll wheel: Zoom
- Click: Select building

**Best for:** Presentations and detailed exploration

---

## Quick Reference

| Tool | Output | Dependencies | Interactive | Best Use Case |
|------|--------|--------------|-------------|---------------|
| `visualize_manifest.py --ascii` | Terminal | None | No | Quick check |
| `visualize_manifest.py --plot` | PNG/PDF | matplotlib | No | Documentation |
| `visualize_manifest.py --html` | HTML | folium | Yes | Detailed maps |
| `create_simple_html_map.py` | HTML | None | Yes | Easy sharing |
| `create_3d_viewer.py` | HTML | None | Yes | 3D exploration |

## Installation

### No Dependencies Required
These tools work out of the box:
- `visualize_manifest.py --ascii`
- `create_simple_html_map.py`
- `create_3d_viewer.py`

### Optional Dependencies
For additional formats:
```bash
pip install matplotlib folium
```

## Examples

### Generate All Visualizations
```bash
# Generate terrain
python generate_urban_terrain.py --bbox 47.6080 47.6060 -122.3340 -122.3360 --format glb

# Create all visualizations
python tools/visualize_manifest.py output/manifest.json --all
python tools/create_simple_html_map.py output/manifest.json -o output/map.html
python tools/create_3d_viewer.py output/manifest.json -o output/viewer.html
```

### Batch Process Multiple Outputs
```bash
# Process all manifest files
for manifest in output_*/manifest.json; do
    dir=$(dirname "$manifest")
    python tools/create_simple_html_map.py "$manifest" -o "$dir/map.html"
done
```

## See Also

- [VISUALIZATION_GUIDE.md](../VISUALIZATION_GUIDE.md) - Detailed documentation
- [QUICKSTART_VISUALIZATION.md](../QUICKSTART_VISUALIZATION.md) - Quick reference
- [examples/](../examples/) - Example output with visualizations
