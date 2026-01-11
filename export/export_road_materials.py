"""
Create road material mapping for thermal property assignment
"""
import json
from pathlib import Path
from typing import Dict, List


def create_road_material_groups(roads_dict: Dict[str, dict]) -> Dict[str, List[str]]:
    """
    Group roads by surface material type for thermal property assignment.

    Args:
        roads_dict: Dictionary of road data from manifest

    Returns:
        Dictionary mapping material types to lists of road IDs
    """
    material_groups = {}

    for road_id, road_data in roads_dict.items():
        properties = road_data.get('properties', {})
        material = properties.get('surface_material', 'asphalt_road')

        if material not in material_groups:
            material_groups[material] = []

        material_groups[material].append(road_id)

    return material_groups


def get_thermal_properties(material: str) -> dict:
    """
    Get typical thermal properties for road surface materials.

    Args:
        material: Standardized material name

    Returns:
        Dictionary with thermal properties
    """
    # Thermal properties reference data
    # Values are approximate and should be adjusted based on specific conditions
    thermal_properties = {
        'asphalt_road': {
            'thermal_conductivity': 0.75,  # W/(m·K)
            'specific_heat': 920,  # J/(kg·K)
            'density': 2300,  # kg/m³
            'emissivity': 0.93,
            'solar_absorptivity': 0.90,  # Dark surface
            'albedo': 0.10,
            'description': 'Asphalt concrete pavement'
        },
        'concrete_road': {
            'thermal_conductivity': 1.4,
            'specific_heat': 880,
            'density': 2300,
            'emissivity': 0.88,
            'solar_absorptivity': 0.65,  # Light colored
            'albedo': 0.35,
            'description': 'Portland cement concrete pavement'
        },
        'concrete_walkway': {
            'thermal_conductivity': 1.4,
            'specific_heat': 880,
            'density': 2300,
            'emissivity': 0.88,
            'solar_absorptivity': 0.60,
            'albedo': 0.40,
            'description': 'Concrete sidewalk/walkway'
        },
        'brick_paved': {
            'thermal_conductivity': 0.72,
            'specific_heat': 840,
            'density': 1800,
            'emissivity': 0.90,
            'solar_absorptivity': 0.75,
            'albedo': 0.25,
            'description': 'Brick or paving stone surface'
        },
        'cobblestone': {
            'thermal_conductivity': 2.2,
            'specific_heat': 790,
            'density': 2500,
            'emissivity': 0.85,
            'solar_absorptivity': 0.70,
            'albedo': 0.30,
            'description': 'Natural stone cobblestone'
        },
        'gravel': {
            'thermal_conductivity': 0.52,
            'specific_heat': 850,
            'density': 1600,
            'emissivity': 0.92,
            'solar_absorptivity': 0.70,
            'albedo': 0.30,
            'description': 'Compacted gravel surface'
        },
        'dirt': {
            'thermal_conductivity': 0.25,
            'specific_heat': 800,
            'density': 1500,
            'emissivity': 0.95,
            'solar_absorptivity': 0.75,
            'albedo': 0.25,
            'description': 'Unpaved dirt/earth surface'
        },
        'grass': {
            'thermal_conductivity': 0.30,
            'specific_heat': 1900,
            'density': 700,
            'emissivity': 0.95,
            'solar_absorptivity': 0.80,
            'albedo': 0.20,
            'description': 'Grass/turf surface'
        },
        'sand': {
            'thermal_conductivity': 0.33,
            'specific_heat': 830,
            'density': 1600,
            'emissivity': 0.90,
            'solar_absorptivity': 0.70,
            'albedo': 0.30,
            'description': 'Sand surface'
        }
    }

    return thermal_properties.get(material, thermal_properties['asphalt_road'])


def save_road_material_mapping(
    roads_dict: Dict[str, dict],
    output_path: str,
    include_thermal_properties: bool = True
):
    """
    Save road material group mappings to a file.

    Args:
        roads_dict: Dictionary of road data from manifest
        output_path: Output file path
        include_thermal_properties: Whether to include thermal property reference data
    """
    material_groups = create_road_material_groups(roads_dict)

    mapping = {
        'description': 'Road surface material assignments for thermal property lookup',
        'groups': material_groups,
        'statistics': {
            material: len(roads) for material, roads in material_groups.items()
        }
    }

    # Add thermal properties reference if requested
    if include_thermal_properties:
        thermal_props = {}
        for material in material_groups.keys():
            thermal_props[material] = get_thermal_properties(material)

        mapping['thermal_properties_reference'] = {
            'description': 'Typical thermal properties for each material type. Adjust based on specific conditions.',
            'materials': thermal_props,
            'notes': [
                'Values are approximate and may vary based on specific composition and conditions',
                'Solar absorptivity and albedo depend on color and surface condition',
                'Thermal conductivity may vary with temperature and moisture content',
                'Use these as starting points and adjust based on calibration data'
            ]
        }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"Road material mapping saved to {output_path}")
    print(f"Material groups: {len(material_groups)}")
    for material, roads in material_groups.items():
        print(f"  {material}: {len(roads)} roads")


if __name__ == "__main__":
    # Test with sample data
    test_roads = {
        'osm_road_123': {
            'type': 'primary',
            'name': '4th Avenue',
            'properties': {
                'surface_material': 'asphalt_road',
                'width_m': 8.0
            }
        },
        'osm_road_456': {
            'type': 'footway',
            'name': None,
            'properties': {
                'surface_material': 'concrete_walkway',
                'width_m': 2.0
            }
        },
        'osm_road_789': {
            'type': 'secondary',
            'name': '3rd Avenue',
            'properties': {
                'surface_material': 'concrete_road',
                'width_m': 7.0
            }
        }
    }

    save_road_material_mapping(test_roads, 'test_road_materials.json')
