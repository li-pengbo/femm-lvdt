import sys
sys.dont_write_bytecode = True
from modules.Helper import *

# Model: aluminum cylinder + magnetic core
path = "../data/alucld/"
filename_template = 'LVDT_alucld_d{outer_str}d{inner_str}_l12_magcore_d{mag_diam_str}_l{mag_len_str}.h5'

outer_diam = [8,10,12,14]

mag_length = [6]
mag_diam = [4]

pairs = generate_pairs(outer_diam,min_thickness=1)

for pair in pairs:
    outer_str = str(pair[0]).zfill(2)
    inner_str = str(pair[1]).zfill(2)
    mag_diam_str = str(mag_diam[0]).zfill(2)
    mag_len_str = str(mag_length[0]).zfill(2)
    filename = filename_template.format(
        outer_str=outer_str,
        inner_str=inner_str,
        mag_diam_str=mag_diam_str,
        mag_len_str=mag_len_str
    )

    print("data will be saved to: ", path + filename)

    simulation_freq = 10000
    simulation_amplitude = 0.02

    Magnet_geo = def_core_geo(mag_diam[0], mag_length[0], 'N40')

    Alu_geo  = def_cylinder_geo(pair[0], pair[1], 12, 'Aluminum, 6061-T6')

    ##########################################################################################################
    OuterCoil_geo  = def_coil_geo("100um", 0.1, 0, 16,  3, 18, 16)
    OC_upper_circuit = def_circuit_prop("outercoil_upper", simulation_freq, simulation_amplitude)
    OC_lower_circuit = def_circuit_prop("outercoil_lower", simulation_freq, -simulation_amplitude)

    MiddleCoil_geo = def_coil_geo("100um", 0.1, 0, 16,  3, 18, 0)
    MC_circuit = def_circuit_prop("middlecoil", 0, 0)


    def_femm_problem(signal_frequency = simulation_freq)
    build_air_geometry("Outside", 10)

    m_label = build_core_geometry(Magnet_geo, 1)
    alu_label = build_cylinder_geometry(Alu_geo, 2)
    mc_label = build_coil_geometry(MiddleCoil_geo, MC_circuit, 3,customized_material=True)
    oc_upper_label = build_coil_geometry(OuterCoil_geo, OC_upper_circuit, 4, customized_material=True )
    oc_lower_label = build_coil_geometry(OuterCoil_geo, OC_lower_circuit, 5, customized_material=True, reverse=True)

    print("Magnet label: ", m_label)
    print("Alu cylinder label: ", alu_label)
    print("Middle coil label: ", mc_label)
    print("Outer coil upper label: ", oc_upper_label)
    print("Outer coil lower label: ", oc_lower_label)
    ##########################################################################################################

    cc_config = def_config(-5, 1,10)
    lvdt_voltage= def_lvdt_voltage(cc_config['steps'])
    sim_results = lvdt_simulation(moving_parts_label  = [1, 2],
                                CC_config           = cc_config,  
                                lvdt_voltage        = lvdt_voltage, 
                                OC_upper_circuit    = OC_upper_circuit,
                                OC_lower_circuit    = OC_lower_circuit,
                                MC_circuit          =MC_circuit,
                                CC_circuit          =None)

    save_data(sim_results, path + filename)

    print("data saved to: ", path + filename)