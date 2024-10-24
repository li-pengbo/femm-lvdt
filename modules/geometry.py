def def_coil_geo(wire_material, wire_diameter, wire_insulation, coil_layer, coil_length, coil_inner_diameter, coil_distance):
    """
    Define the geometry of the coil.
    Args:
    wire_material: str, the material of the wire.
    wire_diameter: float, the diameter of the wire.
    wire_insulation: float, the thickness of the insulation of the wire.
    coil_layer: int, the number of layers of the coil.
    coil_length: float, the length of the coil.
    coil_inner_diameter: float, the inner diameter of the coil.
    coil_distance: float, the distance between the two coils or the distance from the initial position for the moving coil.
    """

    wire_material  = wire_material
    wire_diameter  = wire_diameter
    wire_insulation = wire_insulation
    coil_layer     = coil_layer
    coil_length    = coil_length
    coil_distance = coil_distance # for two coils, it is the distance between the two coils, for one coil, it is the distance from the initial position.
    coil_inner_diameter = coil_inner_diameter
    coil_outer_diameter = coil_inner_diameter + 2 * coil_layer * (wire_diameter + wire_insulation * 2)
    upper_pos = (coil_distance + coil_length) / 2
    lower_pos = (coil_distance - coil_length) / 2
    turns_perlayer = coil_length / (wire_diameter + wire_insulation * 2)
    turns = turns_perlayer * coil_layer
    return {'wire_material': wire_material,
            'wire_diameter': wire_diameter,
            'wire_insulation': wire_insulation,
            'coil_layer': coil_layer,
            'coil_length': coil_length,
            'coil_distance': coil_distance,
            'coil_inner_diameter': coil_inner_diameter,
            'coil_outer_diameter': coil_outer_diameter,
            'upper_pos': upper_pos,
            'lower_pos': lower_pos,
            'turns_perlayer': turns_perlayer,
            'turns': turns}

def def_core_geo(diameter, length, material):
    """
    Define the geometry of the core material.
    Args:
    diameter: float, the diameter of the core.
    length: float, the length of the core.
    material: str, the material of the core.
    shift: float, the initial position shift of the core.
    """
    diameter = diameter
    length = length
    material = material
    upper_pos = length / 2
    lower_pos = -length / 2
    return {'diameter': diameter, 
            'length': length, 
            'material': material, 
            'upper_pos': upper_pos, 
            'lower_pos': lower_pos}

def def_cylinder_geo(inner_diameter, outer_diameter, length, material):
    """
    Define the geometry of the cylinder material.
    Args:
    inner-diameter: float, the inner-diameter of the cylinder.
    outer-diameter: float, the outer-diameter of the cylinder.
    length: float, the length of the cylinder.
    material: str, the material of the cylinder.
    """
    upper_pos = length / 2
    lower_pos = -length / 2
    return {'cldr_inner_diameter':inner_diameter, 
            'cldr_outer_diameter': outer_diameter, 
            'length': length, 
            'material': material,
            'upper_pos': upper_pos, 
            'lower_pos': lower_pos, }

