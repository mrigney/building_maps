# OSM Data Fetch Investigation - Findings

## Problem Summary

The OpenStreetMap data fetching via osmnx is experiencing issues:
1. **Small bounding boxes** → "No buildings found"
2. **Slightly larger boxes** → Hangs indefinitely
3. **Direct Overpass API** → HTTP 504 Gateway Timeout errors

## Root Causes Identified

### 1. Overpass API Server Issues
- The public Overpass API (overpass-api.de) is experiencing timeouts (HTTP 504)
- This appears to be a server-side issue, not a problem with our code
- The API may be overloaded or having reliability issues

### 2. osmnx Library Behavior
- osmnx 2.0+ uses the Overpass API under the hood
- When the API is slow/unreliable, osmnx appears to hang
- The library's timeout settings may not be properly handling server-side timeouts

### 3. Query Area Size Issues
- Even very small areas (100m x 100m) are triggering problems
- The `max_query_area_size` setting we configured may not be taking effect properly
- There appears to be a mismatch between query subdivision and API reliability

## Attempted Solutions

1. ✗ **Increased timeout** - Still hangs
2. ✗ **Reduced area size** - Either no data or hangs
3. ✗ **Direct Overpass API** - Server timeouts (504)
4. ✗ **Conservative settings** - No improvement

## Recommended Solutions

### Option 1: Alternative Overpass Instances
Try using different Overpass API servers:
- `https://overpass.kumi.systems/api/interpreter` (maintained by Kumi Systems)
- `https://overpass.openstreetmap.ru/api/interpreter` (Russian mirror)
- `https://overpass.openstreetmap.fr/api/interpreter` (French mirror)

### Option 2: Use OSM Data Extracts
Download pre-processed OSM data:
- **Geofabrik** (https://download.geofabrik.de/) - Regional extracts
- **BBBike** (https://download.bbbike.org/) - City-specific extracts
- Process locally with ogr2ogr or similar tools

### Option 3: Alternative Data Sources
- **Microsoft Building Footprints** - https://github.com/microsoft/USBuildingFootprints
- **Google Open Buildings** - https://sites.research.google/open-buildings/
- **Local GIS data** - City/county GIS departments often provide building data

### Option 4: Hybrid Approach
1. Use the demo script for immediate testing
2. Implement a retry mechanism with exponential backoff
3. Add support for loading GeoJSON files directly
4. Provide instructions for manual data download

## Immediate Workaround

### For Tonight:
Use the **demo output generator** which works immediately:
```bash
cd urban-terrain-generator
py create_demo_output.py
```

This creates realistic output in ~2-5 seconds with no network calls.

### For Real Data:
I'll implement a solution that:
1. Tries multiple Overpass API instances
2. Falls back to accepting local GeoJSON files
3. Provides clear error messages and retry guidance

## Next Steps (Tomorrow)

1. Implement multi-server Overpass fallback
2. Add GeoJSON file import capability
3. Create helper script to download OSM data extracts
4. Add better error handling and user guidance
5. Document workarounds for API reliability issues

## Testing Notes

- Overpass API status: https://overpass-api.de/api/status
- Test occurred: 2026-01-06 late evening (US time)
- API was returning 504 Gateway Timeouts consistently
- This is likely a temporary infrastructure issue
