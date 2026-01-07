# User Guides

Detailed guides for using the Urban Terrain Generator effectively.

## Available Guides

### 📋 [Workflow Guide](WORKFLOW_GUIDE.md)
**Complete pipeline from geographic data to 3D models**

Learn the full workflow:
- Step-by-step process visualization
- Data acquisition to export
- Using the output in your thermal solver
- Scaling from small to large areas
- Best practices and tips

**Best for**: Understanding the complete system and integration

### 🔍 [Verbose Mode Examples](VERBOSE_EXAMPLE.md)
**Using the --verbose flag for detailed progress**

See the difference between normal and verbose output:
- What verbose mode shows you
- When to use --verbose
- Example commands with verbose output
- Debugging with detailed logs

**Best for**: Troubleshooting and understanding what's happening during OSM fetches

## Quick Examples

### Basic Terrain Generation
```bash
py generate_urban_terrain.py \
  --bbox 47.6097 47.6047 -122.3320 -122.3420 \
  --format glb \
  --instancing
```

### With Verbose Output
```bash
py generate_urban_terrain.py \
  --bbox 47.6097 47.6047 -122.3320 -122.3420 \
  --format glb \
  --instancing \
  --verbose
```

### For Thermal Analysis
```bash
py generate_urban_terrain.py \
  --bbox 47.6097 47.6047 -122.3320 -122.3420 \
  --format ply \
  --instancing \
  --output-dir thermal_analysis
```

## Related Documentation

- **Just starting?** → [Getting Started](../getting-started/)
- **Having issues?** → [Troubleshooting](../troubleshooting/)
- **Technical details?** → [Reference](../reference/)

---

[← Back to Documentation Home](../)
