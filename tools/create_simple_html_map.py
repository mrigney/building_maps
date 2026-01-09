#!/usr/bin/env python3
"""
Create a simple interactive HTML map using only standard libraries and Leaflet.js
No external Python dependencies required!
"""

import json
import argparse
from pathlib import Path


def create_html_map(manifest: dict, output_path: str = "building_map.html"):
    """
    Create an interactive HTML map using Leaflet.js (no Python dependencies).

    Args:
        manifest: Loaded manifest data
        output_path: Path to save HTML file
    """
    buildings = manifest.get('buildings', {})
    metadata = manifest.get('metadata', {})
    bbox = metadata.get('bounding_box', {})

    if not buildings:
        print("No buildings found in manifest")
        return

    # Calculate center
    center_lat = (bbox.get('north', 0) + bbox.get('south', 0)) / 2
    center_lon = (bbox.get('east', 0) + bbox.get('west', 0)) / 2

    # Prepare building data for JavaScript
    building_data = []
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

        building_data.append({
            'id': building_id,
            'lat': lat,
            'lon': lon,
            'height': height,
            'area': area,
            'type': building_type,
            'model': data.get('model_file', 'N/A')
        })

    min_height = min(heights)
    max_height = max(heights)

    # Create HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Urban Terrain Building Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #map {{
            position: absolute;
            top: 0;
            bottom: 0;
            width: 100%;
        }}
        .info-panel {{
            position: absolute;
            top: 10px;
            right: 10px;
            width: 250px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            padding: 15px;
            z-index: 1000;
        }}
        .info-panel h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
            border-bottom: 2px solid #333;
            padding-bottom: 5px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 13px;
        }}
        .legend-color {{
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin-right: 8px;
            border: 1px solid #333;
        }}
        .stats {{
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            font-size: 12px;
        }}
        .stats p {{
            margin: 5px 0;
        }}
        .building-popup {{
            font-family: Arial, sans-serif;
            min-width: 200px;
        }}
        .building-popup h4 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .building-popup table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .building-popup td {{
            padding: 3px 5px;
            font-size: 12px;
        }}
        .building-popup td:first-child {{
            font-weight: bold;
            width: 40%;
        }}
        .height-bar {{
            width: 100%;
            height: 8px;
            background: linear-gradient(to right, #2ecc71, #3498db, #f39c12, #e74c3c);
            margin: 10px 0;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div id="map"></div>

    <div class="info-panel">
        <h3>Building Heights</h3>

        <div class="height-bar"></div>
        <div style="display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 10px;">
            <span>{min_height:.0f}m</span>
            <span>{max_height:.0f}m</span>
        </div>

        <div class="legend-item">
            <div class="legend-color" style="background-color: #2ecc71;"></div>
            <span>< 15m (Low)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #3498db;"></div>
            <span>15-30m (Medium)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #f39c12;"></div>
            <span>30-60m (High)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #e74c3c;"></div>
            <span>> 60m (Very High)</span>
        </div>

        <div class="stats">
            <p><strong>Total Buildings:</strong> {len(buildings)}</p>
            <p><strong>Height Range:</strong> {min_height:.0f}-{max_height:.0f}m</p>
            <p><strong>Mean Height:</strong> {sum(heights)/len(heights):.1f}m</p>
        </div>
    </div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        // Initialize map
        var map = L.map('map').setView([{center_lat}, {center_lon}], 16);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }}).addTo(map);

        // Building data
        var buildings = {json.dumps(building_data, indent=4)};

        // Function to get color based on height
        function getColor(height) {{
            if (height < 15) return '#2ecc71';
            if (height < 30) return '#3498db';
            if (height < 60) return '#f39c12';
            return '#e74c3c';
        }}

        // Add buildings to map
        buildings.forEach(function(building) {{
            var color = getColor(building.height);
            var radius = 5 + (building.height / 10);

            var circle = L.circleMarker([building.lat, building.lon], {{
                radius: radius,
                fillColor: color,
                color: '#333',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.7
            }});

            // Create popup
            var popupContent = `
                <div class="building-popup">
                    <h4>${{building.id}}</h4>
                    <table>
                        <tr><td>Type:</td><td>${{building.type}}</td></tr>
                        <tr><td>Height:</td><td>${{building.height.toFixed(1)}} m</td></tr>
                        <tr><td>Area:</td><td>${{building.area.toFixed(1)}} m²</td></tr>
                        <tr><td>Model:</td><td>${{building.model}}</td></tr>
                    </table>
                </div>
            `;

            circle.bindPopup(popupContent);
            circle.addTo(map);

            // Add height label
            var label = L.marker([building.lat, building.lon], {{
                icon: L.divIcon({{
                    className: 'height-label',
                    html: '<div style="font-size: 9px; color: black; text-shadow: -1px -1px 0 white, 1px -1px 0 white, -1px 1px 0 white, 1px 1px 0 white; font-weight: bold;">' +
                          building.height.toFixed(0) + 'm</div>',
                    iconSize: [30, 10],
                    iconAnchor: [15, -5]
                }})
            }});
            label.addTo(map);
        }});

        // Add bounding box
        var bounds = [
            [{bbox.get('south')}, {bbox.get('west')}],
            [{bbox.get('north')}, {bbox.get('east')}]
        ];
        L.rectangle(bounds, {{
            color: '#e74c3c',
            weight: 2,
            fillOpacity: 0,
            dashArray: '5, 5'
        }}).addTo(map);
    </script>
</body>
</html>"""

    # Save HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Created interactive HTML map: {output_path}")
    print(f"Open the file in your web browser to explore the buildings!")


def main():
    parser = argparse.ArgumentParser(description='Create simple HTML map from manifest.json')
    parser.add_argument('manifest', help='Path to manifest.json file')
    parser.add_argument('--output', '-o', default='building_map.html',
                       help='Output HTML file (default: building_map.html)')

    args = parser.parse_args()

    if not Path(args.manifest).exists():
        print(f"Error: Manifest file not found: {args.manifest}")
        return 1

    print(f"Loading manifest: {args.manifest}")
    with open(args.manifest, 'r') as f:
        manifest = json.load(f)

    create_html_map(manifest, args.output)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
