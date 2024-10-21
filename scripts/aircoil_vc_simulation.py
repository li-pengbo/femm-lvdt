import sys
sys.dont_write_bytecode = True
sys.path.append('../modules/')
from Helper import *

# Model: air coil + magnetic core

path = "../data/"
filename = 'VC_aircoil_magcore_default.h5'

print("data will be saved to: ", path + filename)


simulation_freq = 0
simulation_amplitude = 1

Magnet_geo = def_core_geo(8, 4, 'N40')

OuterCoil_geo  = def_coil_geo("100um", 0.1, 0, 16,
                              3, 18, 16)
OC_upper_circuit = def_circuit_prop("outercoil_upper", simulation_freq, simulation_amplitude)
OC_lower_circuit = def_circuit_prop("outercoil_lower", simulation_freq, -simulation_amplitude)

MiddleCoil_geo = def_coil_geo("100um", 0.1, 0, 16,
                              3, 18, 0)
MC_circuit = def_circuit_prop("middlecoil", 0, 0)

CoreCoil_geo = def_coil_geo("100um",   0.1, 0,  8,
                            12, 12, 0)
CC_circuit = def_circuit_prop("corecoil", 0, 0)

def_femm_problem(signal_frequency = simulation_freq)
build_air_geometry("Outside", 10)

m_label = build_core_geometry(Magnet_geo, 1)
cc_label = build_coil_geometry(CoreCoil_geo, CC_circuit, 2, customized_material=True)
mc_label = build_coil_geometry(MiddleCoil_geo, MC_circuit, 3,customized_material=True)
oc_upper_label = build_coil_geometry(OuterCoil_geo, OC_upper_circuit, 4, customized_material=True )
oc_lower_label = build_coil_geometry(OuterCoil_geo, OC_lower_circuit, 5, customized_material=True, reverse=True)

print("Magnet label: ", m_label)
print("Core coil label: ", cc_label)
print("Middle coil label: ", mc_label)
print("Outer coil upper label: ", oc_upper_label)
print("Outer coil lower label: ", oc_lower_label)


cc_config = def_config(-5, 1,10)
vc_force= def_VC_force(cc_config['steps'])
sim_results = vc_simulation(moving_parts_label  = [1,2],
                            CC_config           = cc_config,  
                            VC_force            = vc_force, 
                            M_label             = m_label, 
                            MC_label            = mc_label, 
                            OC_upper_label      = oc_upper_label, 
                            OC_lower_label      = oc_lower_label)

save_data(sim_results, path + filename)

print("data saved to: ", path + filename)