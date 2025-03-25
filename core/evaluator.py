import sys
sys.path.append('..')
import numpy as np
from core import data_handler
from core.json_handler import JsonHandler
from core.simulator import SimulatorManager

# Parameter modification function
def parameter_modifier(params, input_json, output_json):
    # params: [0: NLI, 1: DI,2: LI,3: NLO,4: DO,5: LO,6: DIO]

    jsonmanager = JsonHandler(input_json=input_json, output_json = output_json)
    jsonmanager.update_config(['coils', 0, 'layers'], params[0])
    jsonmanager.update_config(['coils', 0, 'inner_diameter'], params[1])
    jsonmanager.update_config(['coils', 0, 'bobbin_length'], params[2])

    jsonmanager.update_config(['coils', 1, 'layers'], params[3])
    jsonmanager.update_config(['coils', 1, 'inner_diameter'], params[4])
    jsonmanager.update_config(['coils', 1, 'bobbin_length'], params[5])
    jsonmanager.update_config(['coils', 1, 'offset'], params[6])

    jsonmanager.update_config(['coils', 2, 'layers'], params[3])
    jsonmanager.update_config(['coils', 2, 'inner_diameter'], params[4])
    jsonmanager.update_config(['coils', 2, 'bobbin_length'], params[5])
    jsonmanager.update_config(['coils', 2, 'offset'], -params[6])

    jsonmanager.save_config()

# LVDT Objective function
def lvdt_objective_function(output_dir, output_filename):
    datafile = output_dir + "/" + output_filename
    data_dict = data_handler.load_data(datafile)
    volt_data = data_handler.get_lvdt_data(data_dict, data_type='voltage', flip_sign=False)
    
    position = volt_data['position']
    pickup_voltage_1= (volt_data['Lower_OutCoil']['voltage_abs'])
    pickup_voltage_2= (volt_data['Upper_OutCoil']['voltage_abs'])   
    pickup_voltage = pickup_voltage_2-pickup_voltage_1

    f1= data_handler.sensitivity(position, pickup_voltage)        
    f2= data_handler.non_linear_index(position, pickup_voltage)
    return f1, f2

# VC Objective function
def vc_objective_function(output_dir, output_filename):
    datafile = output_dir + "/" + output_filename
    data_dict = data_handler.load_data(datafile)
    vc_data = data_handler.get_vc_data(data_dict)

    position = vc_data['position']
    lower_Coil_force = vc_data['Lower_OutCoil']['force']
    upper_Coil_force = vc_data['Upper_OutCoil']['force']
    tot_force = np.abs(lower_Coil_force + upper_Coil_force)

    f3 = data_handler.max_force(position, tot_force)
    f4 = data_handler.force_variation_index(position, tot_force)
    return f3, f4

# LVDT evaluation function
def lvdt_evaluator(params,input_json_filename, iter_json_filename, output_dir, output_filename, 
                   auto_close = True, auto_save = False, density_plot = False, gui = False):

    parameter_modifier(params, input_json_filename, iter_json_filename)
    try:
        simulator = SimulatorManager(
            input_jsonname=iter_json_filename, 
            output_filename=output_filename, 
            output_dir=output_dir, 
            auto_close=auto_close,
            auto_save=auto_save,
            density_plot=density_plot,
            gui = gui
            )
        simulator.run_simulation()
    except Exception as e:
        print(f"Error: {e}")
        return -1e6, 1e6
    
    return lvdt_objective_function(output_dir, output_filename)

# VC evaluation function
def vc_evaluator(params, input_json_filename, iter_json_filename, output_dir, output_filename,
                 auto_close = True, auto_save = False, density_plot = False, gui = False):

    parameter_modifier(params, input_json_filename, iter_json_filename)
    try:
        simulator = SimulatorManager(
            input_jsonname=iter_json_filename, 
            output_filename=output_filename,
            output_dir=output_dir, 
            auto_close=auto_close,
            auto_save=auto_save,
            density_plot=density_plot,
            gui = gui
            )
        simulator.run_simulation()
    except Exception as e:
        return e, e
        return -1e6, 1e6
    
    return vc_objective_function(output_dir, output_filename)