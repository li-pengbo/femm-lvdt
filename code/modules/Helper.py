import os
import sys
import femm
import h5py
import numpy as np
sys.dont_write_bytecode = True

def def_femm_problem(signal_frequency = 10000,unit = 'millimeters', problem_type = 'axi', precision = 1e-10):    
    femm.openfemm()
    femm.newdocument(0)
    return def_problem_type(signal_frequency, unit, problem_type, precision)

def def_problem_type(signal_frequency,  unit = 'millimeters', problem_type = 'axi', precision = 1e-10):
    """
    Define the problem type.
    Args:
    signal_frequency: float, the frequency of the signal.
    unit: str, the unit of the geometry.
    problem_type: str, the type of the problem.
    precision: float, the precision of the problem.
    """
    femm.mi_probdef(signal_frequency, unit, problem_type, precision)
    return {'signal_frequency': signal_frequency, 'unit': unit, 'problem_type': problem_type, 'precision': precision}

def def_material(material_name, *args):
    """
    Define the customized material properties for wires, cores, and cylinders.
    """
    if material_name == '100um':
        femm.mi_addmaterial(material_name, 1, 1, 0, 0, 58, 0, 0, 1, 3, 0, 0, 1, 0.1)
    else:
        print("Material not found")
def def_circuit_prop(name, frequency, current):
    """
    Define the circuit properties.
    Args:
    name: str, the name of the circuit.
    frequency: float, the frequency of the circuit.
    current: float, the current of the circuit.
    """
    return {'name': name, 'frequency': frequency, 'current': current}
# def the geometry of the different components
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

def build_coil_geometry(geo_obj, circuit_obj, group_label, customized_material = False, reverse = False):
    """
    Build the geometry of the coil.
    Args:
    geo_obj: dict, the geometry of the coil.
    circuit_obj: dict, the circuit properties.
    group_label: int, the label of the group.
    customized_material: bool, whether the material is customized.
    reverse: bool, whether to reverse the geo position for the symmetric coils.
    """
    if reverse:
        geo_obj['upper_pos'], geo_obj['lower_pos'] = -1 * geo_obj['lower_pos'], -1* geo_obj['upper_pos']

    femm.mi_drawrectangle(geo_obj['coil_inner_diameter'] / 2, geo_obj['lower_pos'], geo_obj['coil_outer_diameter'] / 2, geo_obj['upper_pos'])
    femm.mi_addcircprop(circuit_obj['name'], circuit_obj['current'], 1)
    femm.mi_clearselected()
    femm.mi_selectrectangle(geo_obj['coil_inner_diameter'] / 2, geo_obj['lower_pos'], geo_obj['coil_outer_diameter'] / 2, geo_obj['upper_pos'], 4)
    femm.mi_setgroup(group_label)
    femm.mi_clearselected()
    femm.mi_addblocklabel(geo_obj['coil_inner_diameter'] / 2 + (geo_obj['coil_outer_diameter'] - geo_obj['coil_inner_diameter']) / 4, (geo_obj['upper_pos'] + geo_obj['lower_pos']) / 2)
    femm.mi_selectlabel(geo_obj['coil_inner_diameter'] / 2 + (geo_obj['coil_outer_diameter'] - geo_obj['coil_inner_diameter']) / 4, (geo_obj['upper_pos'] + geo_obj['lower_pos']) / 2)
    
    if customized_material:
        def_material(geo_obj['wire_material'])
    else:
        femm.mi_getmaterial(geo_obj['wire_material'])

    femm.mi_setblockprop(geo_obj['wire_material'], 0, 0.1, circuit_obj['name'], 0, group_label, geo_obj['turns'])
    femm.mi_clearselected()
    return group_label

def build_core_geometry(geo_obj, group_label):
    """
    Build the geometry of the core.
    Args:
    geo_obj: dict, the geometry of the core.
    group_label: int, the label of the group.
    """
    femm.mi_drawrectangle(0, geo_obj['lower_pos'], geo_obj['diameter'] / 2, geo_obj['upper_pos'])
    femm.mi_getmaterial(geo_obj['material'])
    femm.mi_clearselected()
    femm.mi_selectrectangle(0, geo_obj['lower_pos'], geo_obj['diameter'] / 2, geo_obj['upper_pos'], 4)
    femm.mi_setgroup(group_label)
    femm.mi_addblocklabel(geo_obj['diameter'] / 4, (geo_obj['upper_pos'] + geo_obj['lower_pos']) / 2)
    femm.mi_selectlabel(geo_obj['diameter'] / 4, (geo_obj['upper_pos'] + geo_obj['lower_pos']) / 2)
    femm.mi_setblockprop(geo_obj['material'], 0, 0.1, "", 90, group_label, 0)
    femm.mi_clearselected()
    return group_label

def build_cylinder_geometry(geo_obj, group_label):
    """
    Build the geometry of the cylinder.
    Args:
    geo_obj: dict, the geometry of the cylinder.
    group_label: int, the label of the group.
    """
    femm.mi_drawrectangle(geo_obj['cldr_inner_diameter'] / 2, geo_obj['lower_pos'], geo_obj['cldr_outer_diameter'] / 2, geo_obj['upper_pos'])
    femm.mi_getmaterial(geo_obj['material'])
    femm.mi_clearselected()
    femm.mi_selectrectangle(geo_obj['cldr_inner_diameter'] / 2, geo_obj['lower_pos'], geo_obj['cldr_outer_diameter'] / 2, geo_obj['upper_pos'], 4)
    femm.mi_setgroup(group_label)
    femm.mi_clearselected()
    femm.mi_addblocklabel(geo_obj['cldr_inner_diameter'] / 2 + (geo_obj['cldr_outer_diameter'] - geo_obj['cldr_inner_diameter']) / 4, (geo_obj['upper_pos'] + geo_obj['lower_pos']) / 2)
    femm.mi_selectlabel(geo_obj['cldr_inner_diameter'] / 2 + (geo_obj['cldr_outer_diameter'] - geo_obj['cldr_inner_diameter']) / 4, (geo_obj['upper_pos'] + geo_obj['lower_pos']) / 2)
    femm.mi_setblockprop(geo_obj['material'], 0, 0.1, "", 0, group_label, 0)
    return group_label

def build_air_geometry(group_name, group_label):
    """
    Build the geometry of the air.
    Args:
    group_name: str, the name of the group.
    group_label: int, the label of the group.
    """
    # AirSurrounding Structure
    AirSpaceRadius_1 = 100
    AirSpaceRadius_2 = 300
    # Airspace1
    femm.mi_drawline(0, AirSpaceRadius_1, 0, -AirSpaceRadius_1)
    femm.mi_drawarc(0, -AirSpaceRadius_1, 0, AirSpaceRadius_1, 180, 2)
    femm.mi_getmaterial("Air")       
    femm.mi_clearselected()
    femm.mi_addblocklabel(AirSpaceRadius_1/4, AirSpaceRadius_1/2)
    femm.mi_selectlabel(  AirSpaceRadius_1/4, AirSpaceRadius_1/2)
    femm.mi_setblockprop("Air", 0, 0.5, '', 0, 0, 0)
    femm.mi_clearselected()
    # Airspace2              
    femm.mi_drawline(0, AirSpaceRadius_2, 0, -AirSpaceRadius_2)
    femm.mi_drawarc(0, -AirSpaceRadius_2, 0, AirSpaceRadius_2, 180, 2)
    femm.mi_getmaterial("Air")  
    femm.mi_clearselected()
    femm.mi_addblocklabel(AirSpaceRadius_2/2, AirSpaceRadius_2/1.2)
    femm.mi_selectlabel(  AirSpaceRadius_2/2, AirSpaceRadius_2/1.2)
    femm.mi_setblockprop("Air", 1, 0, '', 0, 0, 0)
    femm.mi_clearselected()
    # Boundary properties
    femm.mi_addboundprop(group_name, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    femm.mi_clearselected()
    femm.mi_selectarcsegment(0, AirSpaceRadius_2)
    femm.mi_setarcsegmentprop(2, group_name, 0, group_label)               
    femm.mi_clearselected()

def def_config(init_position, step_size, steps):
    """
    Define the config for the moving coil.
    Args:
    init_position: float, the initial position of the moving coil.
    step_size: float, the size of the step.
    steps: int, the number of steps
    """
    return {'init_position': init_position, 'step_size': step_size, 'steps': steps}

def def_lvdt_voltage(num):
    """
    Define the LVDT voltages variables.
    Args:
    num: int, the number of moving steps.
    Return:
    dict, the LVDT voltage variables, include:
    CC_pos: complex, the position of the moving coil.
    CC_volt: complex, the voltage of the moving coil.
    MC_volt: complex, the voltage of the core coil.
    OC_low_volt: complex, the voltage of the lower outer coil.
    OC_upp_volt: complex, the voltage of the upper outer coil.
    """
    num = num + 1
    return {
        'CC_pos': np.zeros(num).astype(complex),
        'CC_volt': np.zeros(num).astype(complex),
        'MC_volt': np.zeros(num).astype(complex),
        'OC_low_volt': np.zeros(num).astype(complex),
        'OC_upp_volt': np.zeros(num).astype(complex)
    }

def def_VC_force(num):
    num = num + 1
    return {
        'CC_pos': np.zeros(num).astype(complex),
        'M_force': np.zeros(num).astype(complex),
        'MC_force': np.zeros(num).astype(complex),
        'OC_low_force': np.zeros(num).astype(complex),
        'OC_upp_force': np.zeros(num).astype(complex)
    }

def lvdt_simulation(moving_parts_label, CC_config, lvdt_voltage, OC_upper_circuit = None, OC_lower_circuit = None, MC_circuit = None, CC_circuit = None):
    try:
        for i in moving_parts_label:
            femm.mi_selectgroup(i)

        femm.mi_movetranslate(0, CC_config['init_position'])
        femm.mi_clearselected()

        for i in range(0,CC_config['steps']+1):
            print(CC_config['init_position'] + CC_config['step_size']*i)
            lvdt_voltage['CC_pos'][i] = CC_config['init_position'] + CC_config['step_size']*i

            # Now, the finished input geometry can be displayed.
            #femm.mi_zoomnatural()
            femm.mi_zoom(-2,-50,50,50)
            femm.mi_refreshview()

            # We have to give the geometry a name before we can analyze it.
            sim_dir = "sim_files"
            if not os.path.exists(sim_dir):
                os.makedirs(sim_dir)
            # femm.mi_saveas('sim_files/FEMM_lvdt_function.fem')
            femm.mi_saveas(os.path.join(sim_dir, 'FEMM_lvdt_function.fem'))
            # Now,analyze the problem and load the solution when the analysis is finished
            femm.mi_analyze()
            femm.mi_loadsolution()

            if lvdt_voltage['CC_pos'][i] == 0:
                # Show Density Plot:
                femm.mo_showdensityplot(1, 0.0001, 0.0001, 1.0E-9, "bmag")
                        #--legend,	(0=hide, 1=show)
                        #--gscale,	(0=color, 1=greyscale)
                        #--upper_B,	(upperlimit for display)
                        #--lower_B,	(lowerlimit for display)
                        #--type		("bmag", "breal", "bimag" FluxDensity)
                        #--			("hmag", "hreal", "himag" FieldIntensity)
                        #--			("jmag", "jreal", "jimag" CurrentDensity)
                femm.mo_zoom(-2,-50,50,50)
                femm.mo_refreshview()
            OC_upp_i, OC_upp_v, OC_upp_flux = femm.mo_getcircuitproperties(OC_upper_circuit['name'])
            OC_low_i, OC_low_v, OC_low_flux = femm.mo_getcircuitproperties(OC_lower_circuit['name'])
            MC_i, MC_v, MC_flux = femm.mo_getcircuitproperties(MC_circuit['name'])
            
            if CC_circuit:
                CC_i, CC_v, CC_flux = femm.mo_getcircuitproperties(CC_circuit['name'])

            lvdt_voltage['OC_upp_volt'][i] = OC_upp_v
            lvdt_voltage['OC_low_volt'][i] = OC_low_v
            lvdt_voltage['MC_volt'][i] = MC_v
            if CC_circuit:
                lvdt_voltage['CC_volt'][i] = CC_v

            print("OC_upper: I= {:.3f}, V = {:.6f} ".format(OC_upp_i, OC_upp_v))
            print("OC_lower: I= {:.3f}, V = {:.6f} ".format(OC_low_i, OC_low_v))
            print("MiddleCoil: I= {:.3f}, V = {:.6f} ".format(MC_i, MC_v))
            if CC_circuit:
                print("CoreCoil: I= {:.3f}, V = {:.6f} ".format(CC_i, CC_v))
            for i in moving_parts_label:
                femm.mi_selectgroup(i)
            femm.mi_movetranslate(0, CC_config['step_size'])
            femm.mi_clearselected()
        print("Simulation Finished")
        femm.closefemm()
        return lvdt_voltage
    except KeyboardInterrupt:
        print("Simulation Interrupted")

def vc_simulation(moving_parts_label:list, CC_config:dict, VC_force:dict, M_label, MC_label, OC_upper_label, OC_lower_label):
    try:
        for i in moving_parts_label:
            femm.mi_selectgroup(i)

        femm.mi_movetranslate(0, CC_config['init_position'])
        femm.mi_clearselected()

        for i in range(0,CC_config['steps']+1):
            print(CC_config['init_position'] + CC_config['step_size']*i)
            VC_force['CC_pos'][i] = CC_config['init_position'] + CC_config['step_size']*i

            # Now, the finished input geometry can be displayed.
            #femm.mi_zoomnatural()
            femm.mi_zoom(-2,-50,50,50)
            femm.mi_refreshview()

            # We have to give the geometry a name before we can analyze it.
            sim_dir = "sim_files"
            if not os.path.exists(sim_dir):
                os.makedirs(sim_dir)
            # femm.mi_saveas('FEMM_vc_function.fem')
            femm.mi_saveas(os.path.join(sim_dir, 'FEMM_vc_function.fem'))

            # Now,analyze the problem and load the solution when the analysis is finished
            femm.mi_analyze()
            femm.mi_loadsolution()

            if VC_force['CC_pos'][i] == 0:
                # Show Density Plot:
                femm.mo_showdensityplot(1, 0.0001, 0.0001, 1.0E-9, "bmag")
                        #--legend,	(0=hide, 1=show)
                        #--gscale,	(0=color, 1=greyscale)
                        #--upper_B,	(upperlimit for display)
                        #--lower_B,	(lowerlimit for display)
                        #--type		("bmag", "breal", "bimag" FluxDensity)
                        #--			("hmag", "hreal", "himag" FieldIntensity)
                        #--			("jmag", "jreal", "jimag" CurrentDensity)
                femm.mo_zoom(-2,-50,50,50)
                femm.mo_refreshview()

            femm.mo_groupselectblock(OC_upper_label)
            OC_upp_force = femm.mo_blockintegral(19)
            femm.mo_clearblock()

            femm.mo_groupselectblock(OC_lower_label)
            OC_low_force = femm.mo_blockintegral(19)
            femm.mo_clearblock()

            femm.mo_groupselectblock(MC_label)
            MC_force = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            
            femm.mo_groupselectblock(M_label)
            M_force = femm.mo_blockintegral(19)
            femm.mo_clearblock()

            print("Upper Outer Coil: Force = {:.6f} ".format(OC_upp_force))
            print("Lower Outer Coil: Force = {:.6f} ".format(OC_low_force))
            print("MiddleCoil: Force = {:.6f} ".format(MC_force))
            print("Magnet: Force = {:.6f} ".format(M_force))

            VC_force['OC_upp_force'][i] = OC_upp_force
            VC_force['OC_low_force'][i] = OC_low_force
            VC_force['MC_force'][i] = MC_force
            VC_force['M_force'][i] = M_force

            # Translate inner coil to different distance
            for i in moving_parts_label:
                femm.mi_selectgroup(i)
            femm.mi_movetranslate(0, CC_config['step_size'])
            femm.mi_clearselected()
        print("Simulation Finished")
        femm.closefemm()
        return VC_force
    except KeyboardInterrupt:
        print("Simulation Interrupted")

def save_data(data, filename):
    with h5py.File(filename, 'w') as f:
        for key, value in data.items():
            f.create_dataset(key, data=value)

def load_data(filename, show_keys=False):
    with h5py.File(filename, "r") as f:
        keys = list(f.keys())
        if show_keys:
            print("Keys: ", keys)
        return {key: f[key][:] for key in f.keys()}
    
def generate_pairs(outer, min_thickness=2, max_thickness=5):
    pairs = []
    for o in outer:
        max_thickness = int(o / 2)
        for i in range(max(1, o - max_thickness), o - min_thickness + 1):
            pairs.append((o, i))
    return pairs

def process_voltage(data, show_keys=False):
    if 'CC_pos' in data:
        flip_index = len(data['CC_pos'])//2
    if 'MC_volt' in data:
        data['MC_volt_real'] = data['MC_volt'].real
        data['MC_volt_imag'] = data['MC_volt'].imag
        data['MC_volt_abs'] = np.abs(data['MC_volt'])
        data['MC_volt_abs'][:flip_index] = -data['MC_volt_abs'][:flip_index]
    if 'OC_upp_volt' in data:
        data['OC_upp_volt_real'] = data['OC_upp_volt'].real
        data['OC_upp_volt_imag'] = data['OC_upp_volt'].imag
        data['OC_upp_volt_abs'] = np.abs(data['OC_upp_volt'])
        data['OC_upp_volt_abs'][:flip_index] = -data['OC_upp_volt_abs'][:flip_index]
    if 'OC_low_volt' in data:
        data['OC_low_volt_real'] = data['OC_low_volt'].real
        data['OC_low_volt_imag'] = data['OC_low_volt'].imag
        data['OC_low_volt_abs'] = np.abs(data['OC_low_volt'])
        data['OC_low_volt_abs'][:flip_index] = -data['OC_low_volt_abs'][:flip_index]
    if 'CC_volt' in data:
        data['CC_volt_real'] = data['CC_volt'].real
        data['CC_volt_imag'] = data['CC_volt'].imag
        data['CC_volt_abs'] = np.abs(data['CC_volt'])
        data['CC_volt_abs'][:flip_index] = -data['CC_volt_abs'][:flip_index]
    if show_keys:
        print("Keys: ", data.keys())
    return data

