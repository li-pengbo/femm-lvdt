import os
import sys
import femm
import h5py
import numpy as np
from datetime import datetime
from modules import coreConfig, dataHandler, geometry
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

def def_lvdt_data(num):
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
    CC_flux: complex, the flux of the moving coil.
    MC_flux: complex, the flux of the core coil.
    OC_low_flux: complex, the flux of the lower outer coil.
    OC_upp_flux: complex, the flux of the upper outer coil
    """
    num = num + 1
    return {
        'CC_pos': np.zeros(num).astype(complex),
        'CC_volt': np.zeros(num).astype(complex),
        'MC_volt': np.zeros(num).astype(complex),
        'OC_low_volt': np.zeros(num).astype(complex),
        'OC_upp_volt': np.zeros(num).astype(complex),
        'CC_flux': np.zeros(num).astype(complex),
        'MC_flux': np.zeros(num).astype(complex),
        'OC_low_flux': np.zeros(num).astype(complex),
        'OC_upp_flux': np.zeros(num).astype(complex)
    }

def def_vc_data(num):
    num = num + 1
    return {
        'CC_pos': np.zeros(num).astype(complex),
        'M_force': np.zeros(num).astype(complex),
        'MC_force': np.zeros(num).astype(complex),
        'OC_low_force': np.zeros(num).astype(complex),
        'OC_upp_force': np.zeros(num).astype(complex)
    }

def lvdt_simulation(moving_parts_label, CC_config, lvdt_data, OC_upper_circuit = None, OC_lower_circuit = None, MC_circuit = None, CC_circuit = None):
    try:
        for i in moving_parts_label:
            femm.mi_selectgroup(i)

        femm.mi_movetranslate(0, CC_config['init_position'])
        femm.mi_clearselected()

        for i in range(0,CC_config['steps']+1):
            print(CC_config['init_position'] + CC_config['step_size']*i)
            lvdt_data['CC_pos'][i] = CC_config['init_position'] + CC_config['step_size']*i

            # Now, the finished input geometry can be displayed.
            #femm.mi_zoomnatural()
            femm.mi_zoom(-2,-50,50,50)
            femm.mi_refreshview()

            # We have to give the geometry a name before we can analyze it.
            sim_dir = "femm_files"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not os.path.exists(sim_dir):
                os.makedirs(sim_dir)
            femm.mi_saveas(os.path.join(sim_dir,'FEMM_lvdt_function_'+timestamp+'.fem'))
            # Now,analyze the problem and load the solution when the analysis is finished
            femm.mi_analyze()
            femm.mi_loadsolution()

            if lvdt_data['CC_pos'][i] == 0:
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

            lvdt_data['OC_upp_volt'][i] = OC_upp_v
            lvdt_data['OC_low_volt'][i] = OC_low_v
            lvdt_data['MC_volt'][i] = MC_v

            lvdt_data['OC_upp_flux'][i] = OC_upp_flux
            lvdt_data['OC_low_flux'][i] = OC_low_flux
            lvdt_data['MC_flux'][i] = MC_flux

            if CC_circuit:
                lvdt_data['CC_volt'][i] = CC_v
                lvdt_data['CC_flux'][i] = CC_flux

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
        return lvdt_data
    except KeyboardInterrupt:
        print("Simulation Interrupted")

def vc_simulation(moving_parts_label, CC_config, vc_data, M_label, MC_label, OC_upper_label, OC_lower_label):
    try:
        for i in moving_parts_label:
            femm.mi_selectgroup(i)

        femm.mi_movetranslate(0, CC_config['init_position'])
        femm.mi_clearselected()

        for i in range(0,CC_config['steps']+1):
            print(CC_config['init_position'] + CC_config['step_size']*i)
            vc_data['CC_pos'][i] = CC_config['init_position'] + CC_config['step_size']*i

            # Now, the finished input geometry can be displayed.
            #femm.mi_zoomnatural()
            femm.mi_zoom(-2,-50,50,50)
            femm.mi_refreshview()

            # We have to give the geometry a name before we can analyze it.
            sim_dir = "femm_files"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not os.path.exists(sim_dir):
                os.makedirs(sim_dir)
            # femm.mi_saveas('FEMM_vc_function.fem')
            femm.mi_saveas(os.path.join(sim_dir, 'FEMM_vc_function_'+timestamp+'.fem'))

            # Now,analyze the problem and load the solution when the analysis is finished
            femm.mi_analyze()
            femm.mi_loadsolution()

            if vc_data['CC_pos'][i] == 0:
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

            vc_data['OC_upp_force'][i] = OC_upp_force
            vc_data['OC_low_force'][i] = OC_low_force
            vc_data['MC_force'][i] = MC_force
            vc_data['M_force'][i] = M_force

            # Translate inner coil to different distance
            for i in moving_parts_label:
                femm.mi_selectgroup(i)
            femm.mi_movetranslate(0, CC_config['step_size'])
            femm.mi_clearselected()
        print("Simulation Finished")
        femm.closefemm()
        return vc_data
    except KeyboardInterrupt:
        print("Simulation Interrupted")

def run_lvdt_aircoil_simulation(path, filename, simulation_params, core_params, coil_params, customized_material = False):
    """
    Run the LVDT simulation with specified parameters and save the results to a file.

    Parameters:
        path (str): Path to save the data file.
        filename (str): Name of the data file.
        simulation_freq (float): Simulation frequency in Hz.
        simulation_amplitude (float): Amplitude for the outer coil circuit.
        core_params (tuple): Tuple containing parameters for the magnet core.
        coil_params (dict): Dictionary containing parameters for CoreCoil, MiddleCoil, and OuterCoil.
    """
    simulation_freq = simulation_params['frequency']
    simulation_amplitude = simulation_params['amplitude']
    simulation_core = simulation_params['moving_core']

    # Define geometry for core and coils
    if 'magnetcore' in core_params:
        Magnet_geo = geometry.def_core_geo(*core_params['magnetcore'])
    if 'corecoil' in coil_params:
        CoreCoil_geo = geometry.def_coil_geo(*coil_params['corecoil'])
    MiddleCoil_geo = geometry.def_coil_geo(*coil_params['middlecoil'])
    OuterCoil_geo = geometry.def_coil_geo(*coil_params['outercoil'])

    # Define circuit properties
    CC_circuit = None
    if 'corecoil' in coil_params:
        CC_circuit = def_circuit_prop("corecoil", 0, 0)
    MC_circuit = def_circuit_prop("middlecoil", 0, 0)
    OC_upper_circuit = def_circuit_prop("outercoil_upper", simulation_freq, simulation_amplitude)
    OC_lower_circuit = def_circuit_prop("outercoil_lower", simulation_freq, -simulation_amplitude)

    # Set up simulation environment
    def_femm_problem(signal_frequency=simulation_freq)
    build_air_geometry("Outside", 10)

    # Build geometry and assign labels
    m_label = None
    cc_label = None
    if 'magnetcore' in core_params:
        m_label = build_core_geometry(Magnet_geo, 1)
    if 'corecoil' in coil_params:
        cc_label = build_coil_geometry(CoreCoil_geo, CC_circuit, 2, customized_material=customized_material)
    mc_label = build_coil_geometry(MiddleCoil_geo, MC_circuit, 3, customized_material=customized_material)
    oc_upper_label = build_coil_geometry(OuterCoil_geo, OC_upper_circuit, 4, customized_material=customized_material)
    oc_lower_label = build_coil_geometry(OuterCoil_geo, OC_lower_circuit, 5, customized_material=customized_material, reverse=True)
    
    print('m_label:', m_label)
    print('cc_label:', cc_label)
    print('mc_label:', mc_label)
    print('oc_upper_label:', oc_upper_label)
    print('oc_lower_label:', oc_lower_label)
    
    # Simulation configuration
    lvdt_data = def_lvdt_data(simulation_core['steps'])
    moving_parts_label = []
    if 'magnetcore' in core_params:
        moving_parts_label.append(m_label)
    if 'corecoil' in coil_params:
        moving_parts_label.append(cc_label)
    
    if moving_parts_label == []:
        print("No moving parts defined. Please check the core_params.")
        return 0
    # Run the simulation
    sim_results = lvdt_simulation(
        moving_parts_label=moving_parts_label,
        CC_config=simulation_core,
        lvdt_data=lvdt_data,
        OC_upper_circuit=OC_upper_circuit,
        OC_lower_circuit=OC_lower_circuit,
        MC_circuit=MC_circuit,
        CC_circuit=CC_circuit
    )

    # Save results
    dataHandler.save_data(sim_results, path + filename)
    print("Data saved to:", path + filename)
            
def run_lvdt_alucoil_simulation(path, filename, simulation_params, core_params, coil_params, customized_material = False):
    """
    Run the LVDT simulation with specified parameters and save the results to a file.

    Parameters:
        path (str): Path to save the data file.
        filename (str): Name of the data file.
        simulation_freq (float): Simulation frequency in Hz.
        simulation_amplitude (float): Amplitude for the outer coil circuit.
        core_params (tuple): Tuple containing (outer_diameter, inner_diameter) for the magnet geometry.
        coil_params (dict): Dictionary containing parameters for CoreCoil, MiddleCoil, and OuterCoil.
    """
    simulation_freq = simulation_params['frequency']
    simulation_amplitude = simulation_params['amplitude']
    simulation_core = simulation_params['moving_core']

    # Define geometry for core and coils
    if 'magnetcore' in core_params:
        Magnet_geo = geometry.def_core_geo(*core_params['magnetcore'])
    if 'aluminumcylinder' in core_params:
        Alu_geo  = geometry.def_cylinder_geo(*core_params['aluminumcylinder'])
    MiddleCoil_geo = geometry.def_coil_geo(*coil_params['middlecoil'])
    OuterCoil_geo  = geometry.def_coil_geo(*coil_params['outercoil'])
    # Define circuit properties
    MC_circuit = def_circuit_prop("middlecoil", 0, 0)
    OC_upper_circuit = def_circuit_prop("outercoil_upper", simulation_freq, simulation_amplitude)
    OC_lower_circuit = def_circuit_prop("outercoil_lower", simulation_freq, -simulation_amplitude)

    # Set up simulation environment
    def_femm_problem(signal_frequency=simulation_freq)
    build_air_geometry("Outside", 10)

    # Build geometry and assign labels
    m_label = None
    alu_label = None
    if 'magnetcore' in core_params:
        m_label = build_core_geometry(Magnet_geo, 1)
    if 'aluminumcylinder' in core_params:
        alu_label = build_cylinder_geometry(Alu_geo, 2)
    mc_label = build_coil_geometry(MiddleCoil_geo, MC_circuit, 3, customized_material=customized_material)
    oc_upper_label = build_coil_geometry(OuterCoil_geo, OC_upper_circuit, 4, customized_material=customized_material)
    oc_lower_label = build_coil_geometry(OuterCoil_geo, OC_lower_circuit, 5, customized_material=customized_material, reverse=True)

    print("m_label:", m_label)
    print("alu_label:", alu_label)
    print("mc_label:", mc_label)
    print("oc_upper_label:", oc_upper_label)
    print("oc_lower_label:", oc_lower_label)

    # Simulation configuration
    lvdt_data = def_lvdt_data(simulation_core['steps'])
    moving_parts_label = []
    if 'magnetcore' in core_params:
        moving_parts_label.append(m_label)
    if 'aluminumcylinder' in core_params:
        moving_parts_label.append(alu_label)
    if moving_parts_label == []:
        print("No moving parts defined. Please check the core_params.")
        return 0
    # Run the simulation
    sim_results = lvdt_simulation(
        moving_parts_label=moving_parts_label,
        CC_config=simulation_core,
        lvdt_data=lvdt_data,
        OC_upper_circuit=OC_upper_circuit,
        OC_lower_circuit=OC_lower_circuit,
        MC_circuit=MC_circuit,
        CC_circuit=None
    )

    # Save results
    dataHandler.save_data(sim_results, path + filename)
    print("Data saved to:", path + filename)

def run_vc_aircoil_simulation(path, filename, simulation_params, core_params,  coil_params, customized_material = False):
    """
    Run the LVDT simulation with specified parameters and save the results to a file.

    Parameters:
        path (str): Path to save the data file.
        filename (str): Name of the data file.
        simulation_freq (float): Simulation frequency in Hz.
        simulation_amplitude (float): Amplitude for the outer coil circuit.
        core_params (tuple): Tuple containing parameters for the magnet core.
        coil_params (dict): Dictionary containing parameters for CoreCoil, MiddleCoil, and OuterCoil.
    """
    simulation_freq = simulation_params['frequency']
    simulation_amplitude = simulation_params['amplitude']
    simulation_core = simulation_params['moving_core']
    # Define geometry for core and coils
    Magnet_geo = geometry.def_core_geo(*core_params['magnetcore'])
    if 'corecoil' in coil_params:
        CoreCoil_geo = geometry.def_coil_geo(*coil_params['corecoil'])
    MiddleCoil_geo = geometry.def_coil_geo(*coil_params['middlecoil'])
    OuterCoil_geo = geometry.def_coil_geo(*coil_params['outercoil'])

    # Define circuit properties
    CC_circuit = None
    if 'corecoil' in coil_params:
       CC_circuit = def_circuit_prop("corecoil", 0, 0)
    MC_circuit = def_circuit_prop("middlecoil", 0, 0)
    OC_upper_circuit = def_circuit_prop("outercoil_upper", simulation_freq, simulation_amplitude)
    OC_lower_circuit = def_circuit_prop("outercoil_lower", simulation_freq, -simulation_amplitude)

    # Set up simulation environment
    def_femm_problem(signal_frequency=simulation_freq)
    build_air_geometry("Outside", 10)

    # Build geometry and assign labels
    cc_label = None
    m_label = build_core_geometry(Magnet_geo, 1)
    if 'corecoil' in coil_params:
        cc_label = build_coil_geometry(CoreCoil_geo, CC_circuit, 2, customized_material=customized_material)
    mc_label = build_coil_geometry(MiddleCoil_geo, MC_circuit, 3, customized_material=customized_material)
    oc_upper_label = build_coil_geometry(OuterCoil_geo, OC_upper_circuit, 4, customized_material=customized_material)
    oc_lower_label = build_coil_geometry(OuterCoil_geo, OC_lower_circuit, 5, customized_material=customized_material, reverse=True)

    print("Magnet label:", m_label)
    print("Core coil label:", cc_label)
    print("Middle coil label:", mc_label)
    print("Outer coil upper label:", oc_upper_label)
    print("Outer coil lower label:", oc_lower_label)
    
    vc_data = def_vc_data(simulation_core['steps'])
    moving_parts_label = []
    if 'corecoil' in coil_params:
        moving_parts_label.append(cc_label)
    if 'magnetcore' in core_params:
        moving_parts_label.append(m_label)
    if moving_parts_label == []:
        print("No moving parts defined in the simulation, please check the core_params.")
        return 0
    # Run simulation
    sim_results = vc_simulation(
        moving_parts_label=moving_parts_label,
        CC_config=simulation_core,
        vc_data=vc_data,
        M_label=m_label,
        MC_label=mc_label,
        OC_upper_label=oc_upper_label,
        OC_lower_label=oc_lower_label,
    )
    # Save results
    dataHandler.save_data(sim_results, path + filename)
    print("Data saved to:", path + filename)

def run_vc_alucoil_simulation(path, filename, simulation_params, core_params,  coil_params, customized_material = False):
    """
    Run the LVDT simulation with specified parameters and save the results to a file.

    Parameters:
        path (str): Path to save the data file.
        filename (str): Name of the data file.
        simulation_freq (float): Simulation frequency in Hz.
        simulation_amplitude (float): Amplitude for the outer coil circuit.
        core_params (tuple): Tuple containing parameters for the magnet core, aluminum cylinder.
        coil_params (dict): Dictionary containing parameters for CoreCoil, MiddleCoil, and OuterCoil.
    """
    simulation_freq = simulation_params['frequency']
    simulation_amplitude = simulation_params['amplitude']
    simulation_core = simulation_params['moving_core']
    # Define geometry for core and coils
    Magnet_geo = geometry.def_core_geo(*core_params['magnetcore'])
    if 'aluminumcylinder' in core_params:
        Alu_geo = geometry.def_cylinder_geo(*core_params['aluminumcylinder'])
    MiddleCoil_geo = geometry.def_coil_geo(*coil_params['middlecoil'])
    OuterCoil_geo = geometry.def_coil_geo(*coil_params['outercoil'])

    # Define circuit properties
    MC_circuit = def_circuit_prop("middlecoil", 0, 0)
    OC_upper_circuit = def_circuit_prop("outercoil_upper", simulation_freq, simulation_amplitude)
    OC_lower_circuit = def_circuit_prop("outercoil_lower", simulation_freq, -simulation_amplitude)

    # Set up simulation environment
    def_femm_problem(signal_frequency=simulation_freq)
    build_air_geometry("Outside", 10)

    # Build geometry and assign labels
    alu_label = None
    m_label = build_core_geometry(Magnet_geo, 1)
    if 'aluminumcylinder' in core_params:
        alu_label = build_cylinder_geometry(Alu_geo, 2)
    mc_label = build_coil_geometry(MiddleCoil_geo, MC_circuit, 3, customized_material=customized_material)
    oc_upper_label = build_coil_geometry(OuterCoil_geo, OC_upper_circuit, 4, customized_material=customized_material)
    oc_lower_label = build_coil_geometry(OuterCoil_geo, OC_lower_circuit, 5, customized_material=customized_material, reverse=True)

    print("m_label:", m_label)
    print("alu_label:", alu_label)
    print("mc_label:", mc_label)
    print("oc_upper_label:", oc_upper_label)
    print("oc_lower_label:", oc_lower_label)
    
    vc_data = def_vc_data(simulation_core['steps'])
    moving_parts_label = []
    if 'magnetcore' in core_params:
        moving_parts_label.append(m_label)
    if 'aluminumcylinder' in core_params:
        moving_parts_label.append(alu_label)
    if moving_parts_label == []:
        print("No moving parts specified, please check the core_params.")
        return 0

    sim_results = vc_simulation(
        moving_parts_label=moving_parts_label,
        CC_config=simulation_core,
        vc_data=vc_data,
        M_label=m_label, 
        MC_label=mc_label,
        OC_upper_label=oc_upper_label,
        OC_lower_label=oc_lower_label,
    )
    # Save results
    dataHandler.save_data(sim_results, path + filename)
    print("Data saved to:", path + filename)