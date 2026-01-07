# Workflow Guide - From Geographic Data to 3D Terrain

This guide shows the complete workflow from input coordinates to usable 3D terrain models.

## Step-by-Step Process

### Step 1: Define Your Area of Interest

**Input:** Bounding box coordinates (North, South, East, West)

```
Example: Downtown Seattle
┌────────────────────────────────────┐
│ North: 47.6097°                    │
│ South: 47.6047°                    │
│ East:  -122.3320°                  │
│ West:  -122.3420°                  │
│                                    │
│ Area: ~0.5 km × 0.5 km = 0.25 km² │
└────────────────────────────────────┘
```

**Tools:**
- [bboxfinder.com](http://bboxfinder.com)
- [OpenStreetMap Export](https://www.openstreetmap.org/export)

---

### Step 2: Fetch Building Data

**What happens:**
```
User coordinates
      ↓
OpenStreetMap API (via osmnx)
      ↓
Building footprints (2D polygons)
  + metadata (height, type, etc.)
```

**Data retrieved:**
- Building footprints (2D polygons in lat/lon)
- Building heights (from OSM tags like `height=25m` or `building:levels=8`)
- Building types (residential, commercial, etc.)
- Materials (if available in OSM)

**Example data:**
```
Building ID: osm_123456
Footprint: Polygon[(47.6075, -122.3365), (47.6076, -122.3365), ...]
Height: 25.5 meters
Type: commercial
```

---

### Step 3: Coordinate Transformation

**Problem:** Geographic coordinates (lat/lon) aren't suitable for 3D modeling

**Solution:** Convert to local Cartesian coordinates

```
Geographic (lat/lon)          Local Meters
━━━━━━━━━━━━━━━━━━━━    →    ━━━━━━━━━━━━━━━━━━

  N (47.6097°, -122.3370°)         Y
  ↑                                ↑
  │                                │
  │    * Building                  │    * Building
  │                                │      (X: 50m, Y: 100m)
  │                                │
  └────→ E                         └────→ X
Origin (47.6072°, -122.3370°)    Origin (0, 0)

+Z = Up (height)
```

**Benefits:**
- Easy distance calculations in meters
- Simple 3D modeling
- Compatible with most simulation software
- Human-readable coordinates

---

### Step 4: 3D Extrusion

**Transform 2D footprints into 3D buildings:**

```
2D Footprint                    3D Building
━━━━━━━━━━━                    ━━━━━━━━━━━━━

    C────D                          C'───D'
    │    │                         ╱│   ╱│
    │    │                        ╱ │  ╱ │
    A────B                       A'─┼─B' │
                                 │  C─┼──D
Height: 25m                      │ ╱  │ ╱
                                 │╱   │╱
                                 A────B

                                 Height: 25m
```

**Process:**
1. Take 2D polygon vertices
2. Create bottom face at Z=0
3. Create top face at Z=height
4. Connect vertices to create walls
5. Triangulate all faces

**Result:** Watertight 3D mesh with proper normals

---

### Step 5: Optimization (Optional)

**Without Instancing:**
```
1000 buildings = 1000 separate model files
```

**With Instancing:**
```
1000 buildings grouped by dimensions
  ↓
~50-200 unique prototype models
  ↓
Each prototype referenced multiple times
  ↓
Save ~70% file storage
```

**Example:**
```
Prototype_A (10m × 20m × 30m tall)
  ├─ Building_1 at (50, 100)
  ├─ Building_23 at (200, 150)
  └─ Building_47 at (350, 220)

Prototype_B (15m × 15m × 25m tall)
  ├─ Building_2 at (75, 130)
  └─ Building_19 at (180, 90)
```

---

### Step 6: Export to File Formats

**GLB (Binary glTF):**
```
Building Model
  ├─ Vertices: [(0,0,0), (10,0,0), ...]
  ├─ Faces: [(0,1,2), (2,3,4), ...]
  ├─ Normals: [(0,0,1), ...]
  └─ Materials: (optional)

File size: ~5-50 KB per building
Use case: Visualization, general purpose
```

**PLY:**
```
Building Model
  ├─ Vertices: [(0,0,0), (10,0,0), ...]
  └─ Faces: [(0,1,2), (2,3,4), ...]

File size: ~2-20 KB per building
Use case: Computational analysis, smaller files
```

---

### Step 7: Generate Metadata

**Manifest.json - Master Index:**
```json
{
  "metadata": {
    "coordinate_system": {
      "origin_lat": 47.6072,
      "origin_lon": -122.3370
    }
  },
  "buildings": {
    "osm_123456": {
      "model_file": "osm_123456.glb",
      "position": {"lat": 47.6075, "lon": -122.3365},
      "properties": {
        "height_m": 25.5,
        "building_type": "commercial"
      }
    }
  }
}
```

**Material_mapping.json - For Thermal Properties:**
```json
{
  "groups": {
    "concrete": ["osm_123456", "osm_789012"],
    "brick": ["osm_345678", "osm_901234"],
    "metal": ["osm_567890"]
  }
}
```

---

## Final Output Structure

```
output/
│
├── models/                     Individual 3D building models
│   ├── osm_123456.glb         Building 1 (commercial, 25m tall)
│   ├── osm_789012.glb         Building 2 (residential, 15m tall)
│   ├── osm_345678.glb         Building 3 (commercial, 30m tall)
│   └── ...
│
├── manifest.json               Master index
│   • All building locations
│   • Links to model files
│   • Building properties
│   • Coordinate system info
│
├── material_mapping.json       Material groups
│   • Buildings grouped by material
│   • For thermal property assignment
│
└── combined_scene.glb          (Optional) All buildings in one file
    • Quick visualization
    • Single file import
```

---

## Using the Output in Your Heat Transfer Solver

### Step 1: Parse the Manifest
```python
import json

with open('output/manifest.json', 'r') as f:
    manifest = json.load(f)

origin_lat = manifest['metadata']['coordinate_system']['origin_lat']
origin_lon = manifest['metadata']['coordinate_system']['origin_lon']

buildings = manifest['buildings']
```

### Step 2: Load Geometry Files
```python
import trimesh

for building_id, info in buildings.items():
    model_file = info['model_file']
    mesh = trimesh.load(f'output/models/{model_file}')

    # mesh.vertices contains 3D coordinates in local meters
    # mesh.faces contains triangulated faces
```

### Step 3: Apply Thermal Properties
```python
with open('output/material_mapping.json', 'r') as f:
    materials = json.load(f)

for material_type, building_ids in materials['groups'].items():
    thermal_props = your_material_database[material_type]

    for building_id in building_ids:
        assign_properties(building_id, thermal_props)
```

### Step 4: Run Your Simulation
```python
# Buildings are in local coordinates:
# - Origin at (origin_lat, origin_lon)
# - +X = East (meters)
# - +Y = North (meters)
# - +Z = Up (meters)

run_heat_transfer_simulation(buildings, thermal_properties)
```

---

## Example Command Line Workflow

```bash
# 1. Test installation
py test_installation.py

# 2. View example locations
py example_locations.py

# 3. Generate terrain for small area
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing

# 4. Check output
ls output/models/           # See individual building files
cat output/manifest.json    # View metadata
cat output/material_mapping.json  # View material groups

# 5. Optional: Generate combined scene for visualization
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --combined
```

---

## Scaling Up

### Small Test (Recommended First)
```bash
# ~0.25 km², ~100-200 buildings, ~1 minute
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing
```

### Medium Area
```bash
# ~1 km², ~500-1000 buildings, ~3-5 minutes
py generate_urban_terrain.py --bbox 47.6120 47.6030 -122.3300 -122.3450 --format ply --instancing
```

### Large Area
```bash
# ~4 km², ~2000+ buildings, ~10-15 minutes
py generate_urban_terrain.py --bbox 47.6150 47.6000 -122.3250 -122.3500 --format ply --instancing
```

---

## Troubleshooting Workflow Issues

### Issue: No buildings found
**Check:**
1. Coordinates in correct order: NORTH SOUTH EAST WEST
2. Area contains urban development (use OpenStreetMap to verify)
3. Bounding box not too small (try at least 500m × 500m)

### Issue: Slow performance
**Solutions:**
1. Reduce area size
2. Use `--instancing` flag
3. Check network connection (OSM downloads can be slow)

### Issue: Large file sizes
**Solutions:**
1. Use PLY format instead of GLB
2. Enable instancing
3. Process area in smaller chunks

---

## Summary

```
INPUT                    PROCESS                    OUTPUT
─────                    ───────                    ──────

Bounding Box    →    Fetch from OSM      →    Building Data
                     (footprints + meta)

Building Data   →    Coordinate          →    Local Coordinates
                     Transform                 (meters)

Local Coords    →    3D Extrusion        →    3D Meshes

3D Meshes       →    Optimization        →    Instanced Models
                     (optional)

Instanced       →    Export to           →    GLB/PLY Files
Models               Format

Models +        →    Generate            →    Manifest +
Metadata             Metadata                 Material Mapping
```

**Result:** Geo-specific 3D urban terrain ready for thermal simulation!
