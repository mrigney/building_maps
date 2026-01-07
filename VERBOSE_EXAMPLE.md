# Verbose Mode Example

The `--verbose` flag provides detailed progress information during OSM data fetching, so you can see what's happening instead of waiting in silence.

## Normal Output (without --verbose)

```bash
py generate_urban_terrain.py --bbox 40.7584 40.7574 -73.9684 -73.9694 --format glb
```

**Output:**
```
================================================================================
URBAN TERRAIN GENERATOR
================================================================================
Bounding box: (40.757400, -73.969400) to (40.758400, -73.968400)
Output format: GLB
Instancing: Disabled
Verbose: Disabled
================================================================================

[1/6] Fetching building data from OpenStreetMap...
Fetching buildings from OSM for bbox: (40.7574, -73.9694) to (40.7584, -73.9684)
```

**At this point it appears to hang for 30-120 seconds...**

```
Retrieved 45 buildings
Height statistics: min=10.0m, max=50.0m, mean=25.3m

[2/6] Fetching road network from OpenStreetMap...
...
```

## Verbose Output (with --verbose)

```bash
py generate_urban_terrain.py --bbox 40.7584 40.7574 -73.9684 -73.9694 --format glb --verbose
```

**Output:**
```
================================================================================
URBAN TERRAIN GENERATOR
================================================================================
Bounding box: (40.757400, -73.969400) to (40.758400, -73.968400)
Output format: GLB
Instancing: Disabled
Verbose: Enabled
================================================================================

[1/6] Fetching building data from OpenStreetMap...
  → Querying Overpass API...
  → This may take 30-120 seconds depending on area size and network speed...
  → Fetching buildings from OSM for bbox: (40.7574, -73.9694) to (40.7584, -73.9684)
  → Sending request to Overpass API...
  → Waiting for API response (this may take a while)...
```

**Still waiting, but at least you know it's working...**

```
  → Received response, processing 52 features...
  → Filtered to 45 polygon buildings...
Retrieved 45 buildings
Height statistics: min=10.0m, max=50.0m, mean=25.3m

[2/6] Fetching road network from OpenStreetMap...
  → Querying road network...
  → Fetching roads from OSM for bbox: (40.7574, -73.9694) to (40.7584, -73.9684)
  → Querying road network...
  → Waiting for road network data...
  → Converting graph to GeoDataFrame...
Retrieved 23 road segments

[3/6] Setting up local coordinate system...
Origin: (40.757900, -73.968900)

[4/6] Extruding buildings to 3D geometries...
Extruding 45 buildings...
Successfully extruded 45 buildings

[5/6] Exporting geometries...
Exporting 45 buildings to GLB format...
Successfully exported 45 buildings

[6/6] Generating manifest and material mappings...
Manifest saved to output\manifest.json
Material mapping saved to output\material_mapping.json

================================================================================
GENERATION COMPLETE!
================================================================================
Total buildings: 45
Unique models: 45
Output directory: output
  - Models: output\models
  - Manifest: output\manifest.json
  - Material mapping: output\material_mapping.json
================================================================================
```

## When to Use --verbose

Use the verbose flag when:
- **Testing new areas** - See what's happening during the fetch
- **Debugging issues** - Understand where the process might be failing
- **Large areas** - Know the tool is still working during long downloads
- **Slow networks** - Confirm data is being downloaded

## Example Commands

### Basic with verbose
```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --verbose
```

### With all options
```bash
py generate_urban_terrain.py --bbox 47.6097 47.6047 -122.3320 -122.3420 --format glb --instancing --combined --verbose
```

### For debugging
```bash
py generate_urban_terrain.py --bbox 40.7584 40.7574 -73.9684 -73.9694 --format ply --verbose --output-dir debug_output
```
