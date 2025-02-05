import numpy as np
from typing import Dict, List, Any

_LVDT_SIGNAL = ['current', 'voltage','flux']

_VC_SIGNAL = ['force']

def generate_lvdt_data(coil_names: List[str], config: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    data_dict = {}
    init_position = config['initial_position']
    stepsize = config['stepsize']
    steps = config['steps']

    data_dict['Position'] = np.linspace(init_position, init_position + steps * stepsize, steps + 1)
    
    for coil_name in coil_names:
        data_dict[coil_name] = {}
        for signal in _LVDT_SIGNAL:
            data_dict[coil_name][signal] = np.zeros(steps+1, dtype=complex)
    return data_dict

def generate_vc_data(coil_names: List[str], config: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    data_dict = {}
    init_position = config['initial_position']
    stepsize = config['stepsize']
    steps = config['steps']
    
    data_dict['Position'] = np.linspace(init_position, init_position + steps * stepsize, steps + 1)
    
    for coil_name in coil_names:
        data_dict[coil_name] = {}
        for signal in _VC_SIGNAL:
            data_dict[coil_name][signal] = np.zeros(steps+1, dtype=complex)
    return data_dict


    position_values = np.linspace(init_position, init_position + steps * stepsize, steps + 1)
