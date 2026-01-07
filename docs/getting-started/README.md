# Getting Started

Welcome! This section will help you get up and running quickly.

## Start Here

### 🌟 [READ THIS FIRST](READ_THIS_FIRST.md)
**Current status, quick wins, and what you need to know today.**

Perfect for understanding the current state of the project, known issues, and immediate workarounds.

### 📖 [Getting Started Guide](GETTING_STARTED.md)
**Complete installation and first terrain generation.**

Step-by-step instructions to:
- Install dependencies
- Verify installation
- Generate your first terrain
- Understand the output

## Quick Commands

### Install
```bash
pip install -r requirements.txt
py test_installation.py
```

### Generate Demo (No Network Required)
```bash
py create_demo_output.py
```

### Generate Real Terrain
```bash
py generate_urban_terrain.py --bbox NORTH SOUTH EAST WEST --format glb --instancing
```

## What's Next?

After completing the getting started guide:

1. **Explore the output** - Check `demo_output/` or `output/` directories
2. **Read the [Workflow Guide](../guides/WORKFLOW_GUIDE.md)** - Understand the complete pipeline
3. **Try with your data** - Use your own bounding boxes
4. **Integrate** - Connect to your thermal solver

## Need Help?

- **OSM API issues?** → [Troubleshooting](../troubleshooting/)
- **Want more details?** → [Complete Workflow](../guides/WORKFLOW_GUIDE.md)
- **Technical questions?** → [Reference](../reference/)

---

[← Back to Documentation Home](../)
