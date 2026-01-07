# OSM API Issues - Workarounds

**Status**: The OpenStreetMap Overpass API is experiencing reliability issues (HTTP 504 timeouts) as of 2026-01-06.

## Quick Workaround Options

### Option 1: Use the Demo Generator (Immediate)

Generate synthetic building data instantly without any API calls:

```bash
cd urban-terrain-generator
py create_demo_output.py
```

**Output**: 25 buildings in `demo_output/` directory (~2-5 seconds)

This gives you:
- 25 GLB building models
- Complete manifest.json
- Material mapping
- Everything needed to test your thermal solver integration

### Option 2: Download OSM Data Manually

#### Step 1: Download Building Data

**For US Cities:**
Go to https://download.geofabrik.de/north-america/us.html
- Find your state
- Download the `.osm.pbf` or `.shp.zip` file
- Extract building data

**For Other Locations:**
- https://download.geofabrik.de/ (Regional extracts)
- https://download.bbbike.org/ (City-specific)

#### Step 2: Convert to GeoJSON

If you downloaded `.osm.pbf`:
```bash
# Install osmium tool
pip install osmium

# Extract buildings
osmium tags-filter data.osm.pbf w/building -o buildings.osm.pbf

# Convert to GeoJSON
ogr2ogr -f GeoJSON buildings.geojson buildings.osm.pbf lines
```

If you downloaded `.shp.zip`:
```bash
# Already in shapefile format, just convert
ogr2ogr -f GeoJSON buildings.geojson buildings.shp
```

#### Step 3: Use the GeoJSON Loader

```python
from data_acquisition.fetch_from_geojson import load_buildings_from_geojson

buildings_gdf = load_buildings_from_geojson('path/to/buildings.geojson')
```

### Option 3: Use Microsoft Building Footprints

Microsoft provides building footprints for many regions:

#### For US States:
1. Go to: https://github.com/microsoft/USBuildingFootprints
2. Download GeoJSON for your state
3. Load it:

```bash
# Download (example for Washington state)
wget https://usbuildingdata.blob.core.windows.net/usbuildings-v2/Washington.geojson.zip
unzip Washington.geojson.zip

# Use with our tool
py -c "from data_acquisition.fetch_from_geojson import load_buildings_from_geojson; \
       b = load_buildings_from_geojson('Washington.geojson'); \
       print(f'Loaded {len(b)} buildings')"
```

### Option 4: Wait and Retry

The Overpass API issues may be temporary. Check status:
- https://overpass-api.de/api/status
- Try again in a few hours

You can monitor the API health and retry when it's back up.

## Modified Workflow

Until the API issues are resolved, use this workflow:

```bash
# 1. Generate demo data to test your pipeline
py create_demo_output.py

# 2. Test your thermal solver with demo data
# (This proves the output format works)

# 3. Download real data manually (Option 2 or 3 above)

# 4. Load from GeoJSON instead of OSM API
# (Modify your script to use fetch_from_geojson.py)
```

## Future Improvements

I'm working on:
1. **Multi-server fallback** - Try alternative Overpass API servers automatically
2. **Better retry logic** - Exponential backoff with multiple attempts
3. **Caching** - Save successful downloads for reuse
4. **Direct file import** - Make GeoJSON import a first-class option via command line

## Example: Complete Pipeline with GeoJSON

```python
#!/usr/bin/env python3
"""
Modified pipeline using local GeoJSON data
"""
from data_acquisition.fetch_from_geojson import load_buildings_from_geojson
from data_acquisition.fetch_osm import process_building_heights
from geometry.extrude_buildings import extrude_buildings
from export.export_geometry import export_buildings
from export.export_manifest import create_manifest
from utils.geo_utils import get_bounding_box_center

# Load from local file instead of API
buildings_gdf = load_buildings_from_geojson('my_buildings.geojson', verbose=True)

# Process heights
buildings_gdf = process_building_heights(buildings_gdf)

# Set origin (or calculate from data bounds)
origin_lat, origin_lon = 47.6072, -122.3370

# Rest of pipeline works the same
extruded = extrude_buildings(buildings_gdf, origin_lat, origin_lon)
manifest = export_buildings(extruded, 'output/models', format='glb')

print("Done!")
```

## Getting Help

If you need help with any of these workarounds:
1. Check the data_acquisition/fetch_from_geojson.py script
2. Review the demo_output for expected format
3. The investigation findings are in INVESTIGATION_FINDINGS.md

The core functionality works great - it's just the OSM API having issues right now!
