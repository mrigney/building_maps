# Troubleshooting

Solutions for common issues and problems.

## Common Issues

### 🌐 OpenStreetMap API Issues

**Problem**: OSM API hangs, times out, or returns no data

**Solution**: [OSM API Workarounds](OSM_API_WORKAROUND.md)

Multiple workaround options:
- Use demo generator (instant, no network)
- Download OSM data manually
- Use Microsoft Building Footprints
- Import from local GeoJSON files

**Details**: [Investigation Findings](INVESTIGATION_FINDINGS.md)

---

### 🏗️ No Buildings Found

**Symptoms**:
```
ERROR: No buildings found in the specified area!
```

**Possible Causes**:
1. Bounding box coordinates in wrong order
2. Area too small or has no buildings
3. Coordinates in wrong format (DMS instead of decimal degrees)

**Solutions**:
- Verify coordinates: NORTH SOUTH EAST WEST (decimal degrees)
- Try a larger area (0.5-1 km² minimum)
- Check location has buildings on OpenStreetMap.org
- Use `--verbose` to see detailed error messages

---

### 📦 Import Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'osmnx'
```

**Solutions**:
1. Run installation test:
   ```bash
   py test_installation.py
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python version (requires Python 3.8+)

---

### 💾 Memory Issues

**Symptoms**:
- Process crashes with large areas
- System becomes unresponsive

**Solutions**:
- Start with smaller areas (0.25-0.5 km²)
- Use `--instancing` to reduce memory usage
- Export to PLY format (more compact than GLB)
- Close other applications

---

### 🐌 Slow Performance

**Symptoms**:
- OSM fetch takes very long
- Generation process seems stuck

**Solutions**:
1. Use `--verbose` to see progress
2. Check OSM API status: https://overpass-api.de/api/status
3. Try smaller area first
4. Use demo generator to test pipeline: `py create_demo_output.py`
5. Consider manual data download (see OSM workarounds)

---

## Detailed Troubleshooting Guides

### [OSM API Workarounds](OSM_API_WORKAROUND.md)
Complete guide to alternative data sources when OSM API is unavailable:
- Demo generator
- Manual downloads
- Microsoft Building Footprints
- GeoJSON import

### [Investigation Findings](INVESTIGATION_FINDINGS.md)
Technical details on known issues:
- OSM API reliability investigation
- Root cause analysis
- Attempted solutions
- Recommended approaches

---

## Getting More Help

### Before Asking for Help

1. Run `py test_installation.py` to verify setup
2. Try the demo generator: `py create_demo_output.py`
3. Use `--verbose` flag to see detailed output
4. Check if OSM API is operational

### Useful Diagnostic Commands

```bash
# Test installation
py test_installation.py

# Check OSM API access
py -c "import osmnx; print(osmnx.__version__)"

# Generate demo (should work instantly)
py create_demo_output.py

# Test with verbose output
py generate_urban_terrain.py --bbox ... --verbose
```

### Reporting Issues

When reporting issues, include:
- Error message (full output)
- Command you ran
- Bounding box coordinates
- Area size
- Output of `py test_installation.py`

---

## Related Documentation

- **Getting Started** → [Installation & Setup](../getting-started/)
- **User Guides** → [Complete Workflows](../guides/)
- **Reference** → [Technical Details](../reference/)

---

[← Back to Documentation Home](../)
