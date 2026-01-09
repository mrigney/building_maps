#!/usr/bin/env python3
"""
Create an interactive 3D viewer for the generated buildings using Three.js
"""

import json
import argparse
from pathlib import Path


def create_3d_viewer(manifest_path: str, output_path: str = "building_viewer_3d.html"):
    """
    Create an interactive 3D viewer using Three.js.

    Args:
        manifest_path: Path to manifest.json file
        output_path: Path to save HTML file
    """
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    buildings = manifest.get('buildings', {})
    metadata = manifest.get('metadata', {})
    bbox = metadata.get('bounding_box', {})

    if not buildings:
        print("No buildings found in manifest")
        return

    # Get the models directory (relative to manifest)
    manifest_dir = Path(manifest_path).parent
    models_dir = manifest_dir / "models"

    # Prepare building data
    building_data = []
    for building_id, data in buildings.items():
        pos = data.get('position', {})
        props = data.get('properties', {})

        # Convert lat/lon to relative coordinates (simplified)
        # In a real implementation, use proper coordinate transformation
        lat = pos.get('lat')
        lon = pos.get('lon')
        height = props.get('height_m', 0)

        building_data.append({
            'id': building_id,
            'model': f"models/{data.get('model_file')}",
            'lat': lat,
            'lon': lon,
            'height': height,
            'type': props.get('building_type', 'unknown')
        })

    # Calculate center for camera positioning
    center_lat = (bbox.get('north', 0) + bbox.get('south', 0)) / 2
    center_lon = (bbox.get('east', 0) + bbox.get('west', 0)) / 2

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>3D Building Viewer</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        #container {{
            width: 100%;
            height: 100vh;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
            max-width: 300px;
            z-index: 100;
        }}
        #info h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
        }}
        #info p {{
            margin: 5px 0;
            font-size: 12px;
        }}
        #controls {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
            z-index: 100;
        }}
        #controls p {{
            margin: 3px 0;
            font-size: 11px;
        }}
        #loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255, 255, 255, 0.9);
            padding: 20px 40px;
            border-radius: 5px;
            font-size: 18px;
            z-index: 200;
        }}
    </style>
</head>
<body>
    <div id="loading">Loading 3D models...</div>
    <div id="container"></div>

    <div id="info">
        <h3>3D Building Viewer</h3>
        <p><strong>Total Buildings:</strong> {len(buildings)}</p>
        <p><strong>Area:</strong> ({bbox.get('south'):.4f}, {bbox.get('west'):.4f}) to ({bbox.get('north'):.4f}, {bbox.get('east'):.4f})</p>
        <p id="selected-info"></p>
    </div>

    <div id="controls">
        <p><strong>Controls:</strong></p>
        <p>• Left mouse: Rotate</p>
        <p>• Right mouse: Pan</p>
        <p>• Scroll: Zoom</p>
        <p>• Click building: Info</p>
    </div>

    <script type="importmap">
    {{
        "imports": {{
            "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
            "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
        }}
    }}
    </script>

    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
        import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87ceeb); // Sky blue

        const camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            10000
        );

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.getElementById('container').appendChild(renderer.domElement);

        // Orbit controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(100, 200, 100);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        scene.add(directionalLight);

        // Ground plane
        const groundGeometry = new THREE.PlaneGeometry(1000, 1000);
        const groundMaterial = new THREE.MeshStandardMaterial({{
            color: 0x90ee90,
            roughness: 0.8
        }});
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        // Grid helper
        const gridHelper = new THREE.GridHelper(1000, 50, 0x888888, 0xcccccc);
        scene.add(gridHelper);

        // Axes helper
        const axesHelper = new THREE.AxesHelper(100);
        scene.add(axesHelper);

        // Building data
        const buildings = {json.dumps(building_data, indent=4)};

        // Calculate coordinate transformation
        const centerLat = {center_lat};
        const centerLon = {center_lon};
        const metersPerDegreeLat = 111320;
        const metersPerDegreeLon = 111320 * Math.cos(centerLat * Math.PI / 180);

        function latLonToMeters(lat, lon) {{
            const x = (lon - centerLon) * metersPerDegreeLon;
            const y = (lat - centerLat) * metersPerDegreeLat;
            return {{ x, y }};
        }}

        // Load buildings
        const loader = new GLTFLoader();
        let loadedCount = 0;
        const totalBuildings = buildings.length;

        buildings.forEach((building, index) => {{
            const pos = latLonToMeters(building.lat, building.lon);

            // Create placeholder box while loading
            const boxGeometry = new THREE.BoxGeometry(10, building.height, 10);
            const boxMaterial = new THREE.MeshStandardMaterial({{
                color: Math.random() * 0xffffff,
                transparent: true,
                opacity: 0.7
            }});
            const box = new THREE.Mesh(boxGeometry, boxMaterial);
            box.position.set(pos.x, building.height / 2, pos.y);
            box.castShadow = true;
            box.userData = {{
                buildingId: building.id,
                buildingType: building.type,
                height: building.height
            }};
            scene.add(box);

            // Try to load GLB model (will fail if path is incorrect, but placeholder will remain)
            loader.load(
                building.model,
                (gltf) => {{
                    // Remove placeholder
                    scene.remove(box);

                    // Add loaded model
                    const model = gltf.scene;
                    model.position.set(pos.x, 0, pos.y);
                    model.traverse((child) => {{
                        if (child.isMesh) {{
                            child.castShadow = true;
                            child.receiveShadow = true;
                        }}
                    }});
                    model.userData = {{
                        buildingId: building.id,
                        buildingType: building.type,
                        height: building.height
                    }};
                    scene.add(model);

                    loadedCount++;
                    updateLoadingStatus();
                }},
                undefined,
                (error) => {{
                    console.warn(`Could not load model ${{building.model}}, using placeholder`);
                    loadedCount++;
                    updateLoadingStatus();
                }}
            );
        }});

        function updateLoadingStatus() {{
            if (loadedCount >= totalBuildings) {{
                document.getElementById('loading').style.display = 'none';
            }} else {{
                document.getElementById('loading').textContent =
                    `Loading models... ${{loadedCount}}/${{totalBuildings}}`;
            }}
        }}

        // Set camera position
        camera.position.set(200, 150, 200);
        camera.lookAt(0, 0, 0);

        // Raycaster for mouse picking
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function onMouseClick(event) {{
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(scene.children, true);

            if (intersects.length > 0) {{
                const object = intersects[0].object;
                let userData = object.userData;

                // Try to find userData in parent objects
                let parent = object.parent;
                while (parent && !userData.buildingId) {{
                    userData = parent.userData;
                    parent = parent.parent;
                }}

                if (userData.buildingId) {{
                    document.getElementById('selected-info').innerHTML =
                        `<strong>Selected:</strong><br>` +
                        `ID: ${{userData.buildingId}}<br>` +
                        `Type: ${{userData.buildingType}}<br>` +
                        `Height: ${{userData.height.toFixed(1)}}m`;
                }}
            }}
        }}

        window.addEventListener('click', onMouseClick);

        // Handle window resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}

        animate();
    </script>
</body>
</html>"""

    # Save HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Created 3D viewer: {output_path}")
    print(f"Open the file in your web browser to view the 3D scene!")
    print(f"\nNote: The 3D models will load from: {models_dir.relative_to(Path(output_path).parent)}")
    print(f"Make sure the manifest and models are in the correct relative locations.")


def main():
    parser = argparse.ArgumentParser(description='Create 3D viewer from manifest.json')
    parser.add_argument('manifest', help='Path to manifest.json file')
    parser.add_argument('--output', '-o', default='building_viewer_3d.html',
                       help='Output HTML file (default: building_viewer_3d.html)')

    args = parser.parse_args()

    if not Path(args.manifest).exists():
        print(f"Error: Manifest file not found: {args.manifest}")
        return 1

    create_3d_viewer(args.manifest, args.output)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
