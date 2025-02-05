import os
import femm
from datetime import datetime
from models.air  import AirModel
from models.coil import CoilModel
from models.core import CoreModel
from models.shell import ShellModel
from simulation.simulator import BaseSimulator
from simulation.data_generator import generate_lvdt_data

sim = BaseSimulator(signal_frequency = 10000, signal_amplitude=1)

air_space = AirModel(
    group_id = 0,
    boundary_id = 10,
    boundary_name = "Outside",
    inner_radius = 100,
    outer_radius = 300,
    material = "Air",
    is_customized_material = False,
    magdir = 0,
    automesh = 0,
    meshsize = 0.5
)

middle_coil = CoilModel(   
    group_id = 1, 
    inner_diameter=30,
    bobbin_length=3,
    offset=0,
    wire_diameter=0.2,
    insulation=0.0165,
    layers=16,
    wire_material='RS wire',
    is_customized_material=True,
    circuit_name='Middle_Coil',
    circuit_type=1,
    circuit_current=0,
    magdir = 0,
    automesh = 0,
    meshsize = 0.1
)

upper_coil = CoilModel(
    group_id = 2,
    inner_diameter=30,
    bobbin_length=3,
    offset=8,
    wire_diameter=0.2,
    insulation=0.0165,
    layers=16,
    wire_material='RS wire',
    is_customized_material=True,
    circuit_name='Upper_Coil',
    circuit_type=1,
    circuit_current=0.02,
    magdir = 0,
    automesh = 0,
    meshsize = 0.1
)

lower_coil = CoilModel(
    group_id = 3,
    inner_diameter=30,
    bobbin_length=3,
    offset=-8,
    wire_diameter=0.2,
    insulation=0.0165,
    layers=16,
    wire_material='RS wire',
    is_customized_material=True,
    circuit_name='Lower_Coil',
    circuit_type=1,
    circuit_current=-0.02,
    magdir = 0,
    automesh = 0,
    meshsize = 0.1
)

magnet_core = CoreModel(
    group_id = 4,
    diameter=6,
    length = 10,
    offset=0,
    material = 'N40',
    is_customized_material=False,
    magdir = 0,
    automesh = 0,
    meshsize = 0.1
)

aluminum_shell = ShellModel(
    group_id = 5,
    inner_diameter=6,
    outer_diameter=14,
    length = 12,
    offset=0,
    material = 'Aluminum, 6061-T6',
    is_customized_material=False,
    magdir = 0,
    automesh = 0,
    meshsize = 0.1
)

coil_names = [
    middle_coil.get_params['circuit_name'],
    upper_coil.get_params['circuit_name'],
    lower_coil.get_params['circuit_name']
]

moving_elements = [
    magnet_core.get_params['group_id'],
    aluminum_shell.get_params['group_id']
]

config = {
    'initial_position': -5,
    'stepsize': 1,
    'steps': 10,
}

middle_coil_params = middle_coil.get_params
upper_coil_params = upper_coil.get_params
lower_coil_params = lower_coil.get_params
magnet_core_params = magnet_core.get_params
aluminum_shell_params = aluminum_shell.get_params
lvdt_data = generate_lvdt_data(coil_names, config)

sim.initialize()
air_space.build()
middle_coil.build()
upper_coil.build()
lower_coil.build()
magnet_core.build()
aluminum_shell.build()

for element in moving_elements:
    print(f"Moving element {element}")
    femm.mi_selectgroup(element)
femm.mi_movetranslate(0, config['initial_position'])
femm.mi_clearselected()

for i in range(config['steps']):
    print(f"Step {i+1}/{config['steps']}")
    femm.mi_zoom(-2,-50,50,50)
    femm.mi_refreshview()
    sim_dir = "femm_files"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.exists(sim_dir):
        os.makedirs(sim_dir)
    femm.mi_saveas(os.path.join(sim_dir,'lvdt_simulation_'+timestamp+'.fem'))
    femm.mi_analyze()
    femm.mi_loadsolution()

    if lvdt_data['position'][i] == 0:
        femm.mo_showdensityplot(1,0.0001, 0.0001, 1.0e-9, "bmag")
        femm.mo_zoom(-2,-50,50,50)
        femm.mo_refreshview()
    
    for coil in coil_names:
        curr, volt, flux = femm.mo_getcircuitproperties(coil)
        print(f"Coil {coil} - Current: {curr}, Voltage: {volt}, Flux: {flux}")
        lvdt_data[coil]['current'][i] = curr
        lvdt_data[coil]['voltage'][i] = volt
        lvdt_data[coil]['flux'][i] = flux
    
    for j in moving_elements:
        femm.mi_selectgroup(j)
    femm.mi_movetranslate(0, config['stepsize'])
    femm.mi_clearselected()
