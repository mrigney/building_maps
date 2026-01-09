# Building Visualization Guide

This guide explains how to visualize the output from the Urban Terrain Generator using the included visualization tools.

## Overview

After generating urban terrain data with `generate_urban_terrain.py`, you'll have:
- A `manifest.json` file containing building metadata and positions
- Individual GLB model files for each building
- A `material_mapping.json` file

The visualization tools help you explore and understand this data.

---

## Visualization Tools

### 1. Multi-Format Visualizer (`visualize_manifest.py`)

The main visualization tool with multiple output formats.

**Features:**
- ASCII terminal visualization (no dependencies)
- Matplotlib static plots (requires matplotlib)
- Interactive HTML map (requires folium)

**Usage:**

```bash
# Show ASCII visualization in terminal
py visualize_manifest.py output/manifest.json --ascii

# Create matplotlib plot
py visualize_manifest.py output/manifest.json --plot --output building_viz.png

# Create interactive HTML map (requires folium)
py visualize_manifest.py output/manifest.json --html building_map.html

# Generate all visualization types
py visualize_manifest.py output/manifest.json --all
```

**Options:**
- `--ascii` - Show ASCII art in terminal (no dependencies)
- `--plot` - Create matplotlib visualization
- `--html FILE` - Create interactive HTML map with folium
- `--output FILE` - Save matplotlib plot to file
- `--all` - Generate all visualization types
- `--no-show` - Don't display matplotlib plot (just save)

**Dependencies:**
- ASCII mode: None (built-in)
- Plot mode: `matplotlib`
- HTML mode: `folium`

Install dependencies:
```bash
pip install matplotlib folium
```

---

### 2. Simple HTML Map (`create_simple_html_map.py`)

Creates an interactive 2D map using Leaflet.js - **no Python dependencies required!**

**Features:**
- Interactive pan and zoom
- Click buildings for details
- Color-coded by height
- Height labels on each building
- Works in any modern web browser
- Self-contained HTML file

**Usage:**

```bash
py create_simple_html_map.py output/manifest.json --output building_map.html
```

Then open `building_map.html` in your web browser!

**Legend:**
- 🟢 Green: Low buildings (< 15m)
- 🔵 Blue: Medium buildings (15-30m)
- 🟠 Orange: High buildings (30-60m)
- 🔴 Red: Very high buildings (> 60m)

---

### 3. 3D Interactive Viewer (`create_3d_viewer.py`)

Creates a Three.js-based 3D viewer to see your buildings in 3D.

**Features:**
- Interactive 3D navigation
- Loads actual GLB models
- Orbit, pan, and zoom controls
- Click buildings for information
- Ground plane and grid for reference
- Real-time lighting and shadows

**Usage:**

```bash
py create_3d_viewer.py output/manifest.json --output building_viewer_3d.html
```

Then open `building_viewer_3d.html` in your web browser!

**Controls:**
- **Left mouse button**: Rotate view
- **Right mouse button**: Pan view
- **Mouse wheel**: Zoom in/out
- **Click on building**: Show building info

**Note:** The 3D viewer requires the GLB model files to be in the correct location relative to the HTML file. Make sure the `models/` directory is in the same folder as the HTML file.

---

## Example Workflow

1. **Generate terrain data:**
   ```bash
   py generate_urban_terrain.py --bbox 47.6080 47.6060 -122.3340 -122.3360 --format glb
   ```

2. **Quick preview in terminal:**
   ```bash
   py visualize_manifest.py output/manifest.json --ascii
   ```

3. **Create interactive 2D map:**
   ```bash
   py create_simple_html_map.py output/manifest.json --output output/map_2d.html
   ```

4. **Create 3D viewer:**
   ```bash
   py create_3d_viewer.py output/manifest.json --output output/viewer_3d.html
   ```

5. **Open the HTML files in your browser to explore!**

---

## Output Examples

### ASCII Visualization

```
Building Height Map:
  . = < 15m   o = 15-30m   O = 30-60m   # = > 60m

  ------------------------------------------------------------
  |                                                            |
  |                           .                                |
  |                                                            |
  |                o                                           |
  |                                    #                       |
  |                                                            |
  |                       O                                    |
  |                                                 .          |
  ------------------------------------------------------------
```

### 2D Interactive Map

The HTML map shows:
- Building positions on an OpenStreetMap background
- Circle markers sized by building height
- Color-coded height categories
- Click any building to see details
- Legend with statistics

### 3D Viewer

The 3D viewer displays:
- Full 3D scene with all buildings
- Actual GLB models loaded in place
- Ground plane and coordinate grid
- Real-time navigation and interaction
- Building information on click

---

## Visualization Comparison

| Tool | Output | Dependencies | Interactive | Best For |
|------|--------|--------------|-------------|----------|
| `visualize_manifest.py --ascii` | Terminal | None | No | Quick preview |
| `visualize_manifest.py --plot` | PNG/PDF | matplotlib | No | Reports, documentation |
| `visualize_manifest.py --html` | HTML | folium | Yes | Detailed 2D exploration |
| `create_simple_html_map.py` | HTML | None | Yes | Simple 2D sharing |
| `create_3d_viewer.py` | HTML | None | Yes | 3D exploration |

---

## Tips

1. **For presentations**: Use the matplotlib plot mode to create high-quality static images
2. **For exploration**: Use the simple HTML map for quick 2D viewing
3. **For demonstrations**: Use the 3D viewer to show the full terrain
4. **For quick checks**: Use ASCII mode in the terminal
5. **Sharing results**: The HTML files are self-contained and easy to share

---

## Troubleshooting

**Problem**: "Error: folium not installed"
- **Solution**: Use `create_simple_html_map.py` instead, which requires no dependencies

**Problem**: "3D models not loading in viewer"
- **Solution**: Make sure the `models/` folder is in the same directory as the HTML file

**Problem**: "ASCII visualization looks wrong"
- **Solution**: Make sure your terminal supports UTF-8 and has sufficient width (80+ columns)

**Problem**: "Matplotlib plot window is too small"
- **Solution**: The figure is created at 16x8 inches. You can modify the `figsize` parameter in the script

---

## Advanced Usage

### Custom Matplotlib Styling

Edit `visualize_manifest.py` and modify the matplotlib section to customize:
- Colors (change `cmap` parameter)
- Marker sizes (adjust the `s` parameter formula)
- Figure size (modify `figsize`)

### Custom HTML Styling

Edit `create_simple_html_map.py` to customize:
- Color scheme (modify the `getColor()` function)
- Marker sizes (adjust radius calculation)
- Legend content (modify the legend HTML)

### Batch Processing

Create visualizations for multiple manifest files:

```bash
# Process all manifest files
for manifest in output_*/manifest.json; do
    dirname=$(dirname "$manifest")
    py create_simple_html_map.py "$manifest" --output "$dirname/map.html"
done
```

---

## Next Steps

- Try generating terrain for different locations
- Compare building density across regions
- Use the visualizations in presentations or reports
- Integrate the 3D viewer into web applications

For more information, see the main [README.md](README.md) file.
