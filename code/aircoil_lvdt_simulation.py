import sys
sys.dont_write_bytecode = True
from Helper import *

# Model: air coil + magnetic core

path = "../data/"
filename = 'LVDT_aircoil_default.h5'

print("data will be saved to: ", path + filename)

simulation_freq = 10000
simulation_amplitude = 0.02

# Magnet_geo = def_core_geo(8, 4, 'N40', 0)

CoreCoil_geo = def_coil_geo("100um",   0.1, 0,  8, 12, 12, 0)
CC_circuit = def_circuit_prop("corecoil", 0, 0)

MiddleCoil_geo = def_coil_geo("100um", 0.1, 0, 16,  3, 18, 0)
MC_circuit = def_circuit_prop("middlecoil", 0, 0)

OuterCoil_geo  = def_coil_geo("100um", 0.1, 0, 16,  3, 18, 16)
OC_upper_circuit = def_circuit_prop("outercoil_upper", simulation_freq, simulation_amplitude)
OC_lower_circuit = def_circuit_prop("outercoil_lower", simulation_freq, -simulation_amplitude)

def_femm_problem(signal_frequency = simulation_freq)
build_air_geometry("Outside", 10)

# m_label = build_core_geometry(Magnet_geo, 1)
cc_label = build_coil_geometry(CoreCoil_geo, CC_circuit, 2, customized_material=True)
mc_label = build_coil_geometry(MiddleCoil_geo, MC_circuit, 3,customized_material=True)
oc_upper_label = build_coil_geometry(OuterCoil_geo, OC_upper_circuit, 4, customized_material=True )
oc_lower_label = build_coil_geometry(OuterCoil_geo, OC_lower_circuit, 5, customized_material=True, reverse=True)

# print("Magnet label: ", m_label)
print("Core coil label: ", cc_label)
print("Middle coil label: ", mc_label)
print("Outer coil upper label: ", oc_upper_label)
print("Outer coil lower label: ", oc_lower_label)

cc_config = def_config(-5, 1,10)
lvdt_voltage= def_lvdt_voltage(cc_config['steps'])
sim_results = lvdt_simulation(moving_parts_label  = [2],
                              CC_config           = cc_config,  
                              lvdt_voltage        = lvdt_voltage, 
                              OC_upper_circuit    = OC_upper_circuit,
                              OC_lower_circuit    = OC_lower_circuit,
                              MC_circuit          =MC_circuit,
                              CC_circuit          =None)

save_data(sim_results, path + filename)

print("data saved to: ", path + filename)