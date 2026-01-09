#!/usr/bin/env python3
"""
Visualize buildings from manifest.json file

Creates an interactive 2D map showing building locations, heights, and properties.
Supports multiple output formats: matplotlib plot, HTML interactive map, and terminal ASCII.
"""

import json
import argparse
from pathlib import Path
import sys


def load_manifest(manifest_path: str) -> dict:
    """Load manifest.json file."""
    with open(manifest_path, 'r') as f:
        return json.load(f)


def visualize_matplotlib(manifest: dict, output_path: str = None, show: bool = True):
    """
    Create a matplotlib visualization of buildings.

    Args:
        manifest: Loaded manifest data
        output_path: Optional path to save the figure
        show: Whether to display the figure interactively
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.collections import PatchCollection
    except ImportError:
        print("Error: matplotlib not installed. Install with: pip install matplotlib")
        return

    buildings = manifest.get('buildings', {})
    metadata = manifest.get('metadata', {})
    bbox = metadata.get('bounding_box', {})

    if not buildings:
        print("No buildings found in manifest")
        return

    # Extract building data
    lats = []
    lons = []
    heights = []
    areas = []
    labels = []
    types = []

    for building_id, data in buildings.items():
        pos = data.get('position', {})
        props = data.get('properties', {})

        lats.append(pos.get('lat'))
        lons.append(pos.get('lon'))
        heights.append(props.get('height_m', 0))
        areas.append(props.get('area_sqm', 0))
        labels.append(building_id)
        types.append(props.get('building_type', 'unknown'))

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Plot 1: Buildings colored by height
    scatter1 = ax1.scatter(lons, lats, c=heights, s=[a/20 for a in areas],
                          alpha=0.7, cmap='viridis', edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title(f'Building Locations Colored by Height\n({len(buildings)} buildings)')
    ax1.grid(True, alpha=0.3)

    # Add bounding box
    if bbox:
        ax1.axhline(y=bbox.get('north'), color='r', linestyle='--', alpha=0.3, label='Bounding Box')
        ax1.axhline(y=bbox.get('south'), color='r', linestyle='--', alpha=0.3)
        ax1.axvline(x=bbox.get('east'), color='r', linestyle='--', alpha=0.3)
        ax1.axvline(x=bbox.get('west'), color='r', linestyle='--', alpha=0.3)
        ax1.legend()

    # Add colorbar
    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label('Height (m)', rotation=270, labelpad=20)

    # Plot 2: Buildings colored by type
    # Create type to color mapping
    unique_types = list(set(types))
    type_colors = {t: i for i, t in enumerate(unique_types)}
    colors = [type_colors[t] for t in types]

    scatter2 = ax2.scatter(lons, lats, c=colors, s=[a/20 for a in areas],
                          alpha=0.7, cmap='tab10', edgecolors='black', linewidth=0.5)
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.set_title(f'Building Locations Colored by Type\n({len(unique_types)} types)')
    ax2.grid(True, alpha=0.3)

    # Add legend for types
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w',
                             markerfacecolor=plt.cm.tab10(type_colors[t] / len(unique_types)),
                             markersize=8, label=t)
                      for t in unique_types[:10]]  # Limit to 10 types
    ax2.legend(handles=legend_elements, loc='best', fontsize=8)

    # Add statistics
    stats = manifest.get('statistics', {})
    stats_text = f"Total Buildings: {stats.get('total_buildings', len(buildings))}\n"
    stats_text += f"Height Range: {min(heights):.1f}m - {max(heights):.1f}m\n"
    stats_text += f"Mean Height: {sum(heights)/len(heights):.1f}m\n"
    stats_text += f"Total Area: {sum(areas):.1f} m²"

    fig.text(0.5, 0.02, stats_text, ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved visualization to: {output_path}")

    if show:
        plt.show()
    else:
        plt.close()


def visualize_html(manifest: dict, output_path: str = "visualization.html"):
    """
    Create an interactive HTML visualization using Folium.

    Args:
        manifest: Loaded manifest data
        output_path: Path to save HTML file
    """
    try:
        import folium
        from folium import plugins
    except ImportError:
        print("Error: folium not installed. Install with: pip install folium")
        return

    buildings = manifest.get('buildings', {})
    metadata = manifest.get('metadata', {})
    bbox = metadata.get('bounding_box', {})

    if not buildings:
        print("No buildings found in manifest")
        return

    # Calculate center
    center_lat = (bbox.get('north', 0) + bbox.get('south', 0)) / 2
    center_lon = (bbox.get('east', 0) + bbox.get('west', 0)) / 2

    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=16,
        tiles='OpenStreetMap'
    )

    # Add buildings
    heights = []
    for building_id, data in buildings.items():
        pos = data.get('position', {})
        props = data.get('properties', {})

        lat = pos.get('lat')
        lon = pos.get('lon')
        height = props.get('height_m', 0)
        area = props.get('area_sqm', 0)
        building_type = props.get('building_type', 'unknown')

        heights.append(height)

        # Color based on height (normalized)
        if height < 15:
            color = 'green'
        elif height < 30:
            color = 'blue'
        elif height < 60:
            color = 'orange'
        else:
            color = 'red'

        # Create popup
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin: 0 0 10px 0;">{building_id}</h4>
            <table style="width: 100%;">
                <tr><td><b>Type:</b></td><td>{building_type}</td></tr>
                <tr><td><b>Height:</b></td><td>{height:.1f} m</td></tr>
                <tr><td><b>Area:</b></td><td>{area:.1f} m²</td></tr>
                <tr><td><b>Model:</b></td><td>{data.get('model_file', 'N/A')}</td></tr>
            </table>
        </div>
        """

        # Add marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=5 + (height / 10),  # Size based on height
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)

        # Add label
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=f'''
                <div style="font-size: 8pt; color: black;
                            text-shadow: -1px -1px 0 white, 1px -1px 0 white,
                                        -1px 1px 0 white, 1px 1px 0 white;">
                    {height:.0f}m
                </div>
            ''')
        ).add_to(m)

    # Add legend
    legend_html = f'''
    <div style="position: fixed;
                top: 10px; right: 10px; width: 180px;
                background-color: white; z-index:9999;
                border:2px solid grey; border-radius: 5px;
                padding: 10px; font-size: 12px;">
        <h4 style="margin-top: 0;">Building Heights</h4>
        <p style="margin: 5px 0;"><span style="color: green;">●</span> < 15m (Low)</p>
        <p style="margin: 5px 0;"><span style="color: blue;">●</span> 15-30m (Medium)</p>
        <p style="margin: 5px 0;"><span style="color: orange;">●</span> 30-60m (High)</p>
        <p style="margin: 5px 0;"><span style="color: red;">●</span> > 60m (Very High)</p>
        <hr>
        <p style="margin: 5px 0;"><b>Total Buildings:</b> {len(buildings)}</p>
        <p style="margin: 5px 0;"><b>Height Range:</b> {min(heights):.0f}-{max(heights):.0f}m</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add fullscreen option
    plugins.Fullscreen().add_to(m)

    # Save
    m.save(output_path)
    print(f"Saved interactive HTML map to: {output_path}")
    print(f"Open it in your browser to explore the buildings!")


def visualize_ascii(manifest: dict):
    """
    Create a simple ASCII visualization in the terminal.

    Args:
        manifest: Loaded manifest data
    """
    buildings = manifest.get('buildings', {})
    metadata = manifest.get('metadata', {})
    bbox = metadata.get('bounding_box', {})
    stats = manifest.get('statistics', {})

    if not buildings:
        print("No buildings found in manifest")
        return

    print("=" * 80)
    print("BUILDING VISUALIZATION (ASCII)")
    print("=" * 80)
    print()

    # Print statistics
    print(f"Total Buildings: {stats.get('total_buildings', len(buildings))}")
    print(f"Bounding Box: ({bbox.get('south'):.6f}, {bbox.get('west'):.6f}) to "
          f"({bbox.get('north'):.6f}, {bbox.get('east'):.6f})")
    print()

    # Create simple grid
    grid_width = 60
    grid_height = 20

    # Calculate bounds
    min_lat = bbox.get('south', 0)
    max_lat = bbox.get('north', 0)
    min_lon = bbox.get('west', 0)
    max_lon = bbox.get('east', 0)

    # Create grid
    grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

    # Plot buildings
    for building_id, data in buildings.items():
        pos = data.get('position', {})
        props = data.get('properties', {})

        lat = pos.get('lat')
        lon = pos.get('lon')
        height = props.get('height_m', 0)

        # Normalize to grid coordinates
        if max_lat != min_lat and max_lon != min_lon:
            x = int((lon - min_lon) / (max_lon - min_lon) * (grid_width - 1))
            y = int((lat - min_lat) / (max_lat - min_lat) * (grid_height - 1))
            y = grid_height - 1 - y  # Flip y axis

            # Choose symbol based on height
            if height < 15:
                symbol = '.'
            elif height < 30:
                symbol = 'o'
            elif height < 60:
                symbol = 'O'
            else:
                symbol = '#'

            if 0 <= x < grid_width and 0 <= y < grid_height:
                grid[y][x] = symbol

    # Print grid
    print("Building Height Map:")
    print("  . = < 15m   o = 15-30m   O = 30-60m   # = > 60m")
    print()
    print("  " + "-" * grid_width)
    for row in grid:
        print("  |" + "".join(row) + "|")
    print("  " + "-" * grid_width)
    print()

    # Print building list
    print("Building Details:")
    print(f"{'ID':<20} {'Type':<15} {'Height':<10} {'Area (m²)':<12}")
    print("-" * 80)

    for building_id, data in sorted(buildings.items(),
                                   key=lambda x: x[1]['properties'].get('height_m', 0),
                                   reverse=True)[:10]:  # Top 10 by height
        props = data.get('properties', {})
        print(f"{building_id:<20} {props.get('building_type', 'unknown'):<15} "
              f"{props.get('height_m', 0):<10.1f} {props.get('area_sqm', 0):<12.1f}")

    if len(buildings) > 10:
        print(f"... and {len(buildings) - 10} more buildings")

    print()
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Visualize buildings from manifest.json',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show ASCII visualization
  python visualize_manifest.py output/manifest.json --ascii

  # Create interactive HTML map
  python visualize_manifest.py output/manifest.json --html building_map.html

  # Create matplotlib plot and save
  python visualize_manifest.py output/manifest.json --plot --output viz.png

  # All visualizations
  python visualize_manifest.py output/manifest.json --all
        """
    )

    parser.add_argument(
        'manifest',
        help='Path to manifest.json file'
    )

    parser.add_argument(
        '--ascii',
        action='store_true',
        help='Show ASCII visualization in terminal'
    )

    parser.add_argument(
        '--plot',
        action='store_true',
        help='Create matplotlib plot'
    )

    parser.add_argument(
        '--html',
        type=str,
        metavar='FILE',
        help='Create interactive HTML map (requires folium)'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save matplotlib plot to file (requires --plot)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all visualization types'
    )

    parser.add_argument(
        '--no-show',
        action='store_true',
        help='Do not display matplotlib plot interactively'
    )

    args = parser.parse_args()

    # Load manifest
    if not Path(args.manifest).exists():
        print(f"Error: Manifest file not found: {args.manifest}")
        return 1

    print(f"Loading manifest: {args.manifest}")
    manifest = load_manifest(args.manifest)
    print()

    # Determine what to generate
    if args.all:
        args.ascii = True
        args.plot = True
        if not args.html:
            args.html = "building_visualization.html"
        if not args.output:
            args.output = "building_visualization.png"

    # If no options specified, default to ASCII
    if not (args.ascii or args.plot or args.html):
        args.ascii = True

    # Generate visualizations
    if args.ascii:
        visualize_ascii(manifest)
        print()

    if args.plot:
        visualize_matplotlib(manifest, args.output, show=not args.no_show)
        print()

    if args.html:
        visualize_html(manifest, args.html)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
