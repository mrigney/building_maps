# Quick Start: Visualizing Your Buildings

## TL;DR - Fast Commands

Already generated terrain? Here are the fastest ways to visualize it:

### 1. Quick Preview (0 dependencies)
```bash
py visualize_manifest.py output/manifest.json --ascii
```
Shows buildings in your terminal immediately!

### 2. Interactive 2D Map (0 dependencies)
```bash
py create_simple_html_map.py output/manifest.json -o output/map.html
```
Then open `output/map.html` in your browser.

### 3. Interactive 3D View (0 dependencies)
```bash
py create_3d_viewer.py output/manifest.json -o output/3d.html
```
Then open `output/3d.html` in your browser.

---

## What Each Tool Shows

### ASCII Terminal View
```
Building Height Map:
  . = < 15m   o = 15-30m   O = 30-60m   # = > 60m

  ------------------------------------------------------------
  |                           .                                |
  |                o                                           |
  |                                    #                       |
  |                       O                                    |
  ------------------------------------------------------------
```
**Best for:** Quick sanity check

### 2D Interactive Map
- OpenStreetMap background
- Color-coded building markers
- Click for building details
- Height labels
- Pan and zoom

**Best for:** Understanding spatial layout

### 3D Interactive View
- Full 3D scene with actual models
- Orbit camera controls
- Click buildings for info
- Ground plane and grid

**Best for:** Presentations and exploration

---

## Example Workflow

```bash
# 1. Generate buildings for Seattle downtown
py generate_urban_terrain.py --bbox 47.6080 47.6060 -122.3340 -122.3360 --format glb

# 2. Quick check what you got
py visualize_manifest.py output/manifest.json --ascii

# 3. Create shareable visualizations
py create_simple_html_map.py output/manifest.json -o output/map.html
py create_3d_viewer.py output/manifest.json -o output/3d.html

# 4. Open the HTML files in your browser!
```

---

## Which Tool Should I Use?

| Need | Use This |
|------|----------|
| Quick check if generation worked | ASCII terminal view |
| See where buildings are located | 2D HTML map |
| Show someone the 3D models | 3D viewer |
| Static image for report | matplotlib (requires install) |
| Share with non-technical users | HTML files (easy to email) |

---

## No Dependencies Required!

The recommended tools require **zero Python dependencies**:
- `visualize_manifest.py --ascii` - uses only Python standard library
- `create_simple_html_map.py` - creates self-contained HTML with Leaflet.js
- `create_3d_viewer.py` - creates self-contained HTML with Three.js

Just open the HTML files in any modern browser!

---

## Help & More Info

- Full documentation: [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)
- Project README: [README.md](README.md)
- Report issues: Check your console for errors

---

**Created visualization tools for:** Urban Terrain Generator v0.1
