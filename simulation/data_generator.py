# LVDT_simulation/simulation/data_generator.py
import numpy as np
from typing import Dict, List, Any

_LVDT_SIGNAL = ['current', 'voltage','flux']

_VC_SIGNAL = ['force']

def generate_lvdt_data(config: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    data_dict = {}

    init_position = config['simulation']['initial_position']
    stepsize = config['simulation']['stepsize']
    steps = config['simulation']['steps']
    
    data_dict['position'] = np.linspace(init_position, init_position + steps * stepsize, steps + 1)

    coil_names = [coil['circuit_name'] for coil in config['coils']]
    for coil_name in coil_names:
        data_dict[coil_name] = {}
        for signal in _LVDT_SIGNAL:
            data_dict[coil_name][signal] = np.zeros(steps+1, dtype=complex)
    
    return data_dict

def generate_vc_data(config: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    data_dict = {}
    init_position = config['simulation']['initial_position']
    stepsize = config['simulation']['stepsize']
    steps = config['simulation']['steps']
    data_dict['position'] = np.linspace(init_position, init_position + steps * stepsize, steps + 1)

    coil_names = [coil['circuit_name'] for coil in config['coils']]
    core_names = ["core_"+str(core['group_id']) for core in config['cores']]
    shell_names = ["shell_"+str(shell['group_id']) for shell in config['shells']]
    for coil_name in coil_names:
        data_dict[coil_name] = {}
        for signal in _VC_SIGNAL:
            data_dict[coil_name][signal] = np.zeros(steps+1, dtype=complex)
    for core_name in core_names:
        data_dict[core_name] = {}
        for signal in _VC_SIGNAL:
            data_dict[core_name][signal] = np.zeros(steps+1, dtype=complex)
    for shell_name in shell_names:
        data_dict[shell_name] = {}
        for signal in _VC_SIGNAL:
            data_dict[shell_name][signal] = np.zeros(steps+1, dtype=complex)
    
    return data_dict