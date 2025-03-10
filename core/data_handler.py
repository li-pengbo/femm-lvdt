# LVDT_simulation/simulation/data_handler.py
import h5py
import numpy as np
from typing import Dict, List, Any
from scipy.stats import linregress
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

##########################################################
#### Define the data structure for the simulation data####
##########################################################
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

    for coil_name in coil_names:
        data_dict[coil_name] = {}
        for signal in _VC_SIGNAL:
            data_dict[coil_name][signal] = np.zeros(steps+1, dtype=complex)

    if 'cores' in config:
        core_names = ["core_"+str(core['group_id']) for core in config['cores']]
        for core_name in core_names:
            data_dict[core_name] = {}
            for signal in _VC_SIGNAL:
                data_dict[core_name][signal] = np.zeros(steps+1, dtype=complex)
                
    if 'shells' in config:
        shell_names = ["shell_"+str(shell['group_id']) for shell in config['shells']]
        for shell_name in shell_names:
            data_dict[shell_name] = {}
            for signal in _VC_SIGNAL:
                data_dict[shell_name][signal] = np.zeros(steps+1, dtype=complex)
    
    return data_dict
##########################################################
#### Define the method to load the simulation data    ####
##########################################################
def load_h5_to_dict(h5group):
    result = {}
    for key, item in h5group.items():
        if isinstance(item, h5py.Group):  
            result[key] = load_h5_to_dict(item)  
        elif isinstance(item, h5py.Dataset):  
            value = item[()]
            if isinstance(value, bytes):  
                value = value.decode()
            elif isinstance(value, np.ndarray) and value.dtype == np.bytes_:
                value = np.array([v.decode() if isinstance(v, bytes) else v for v in value])
            result[key] = value
    return result

def load_data(file_path: str):
    with h5py.File(file_path, "r") as h5f:
        return {
            "config": load_h5_to_dict(h5f["config"]),
            "data": load_h5_to_dict(h5f["data"])
        }

def get_config_data(data_dict):
    config_data = {}
    
    config_data['simulation'] = data_dict.get("config", {}).get("simulation", {})

    element_mapping = {
        'coils':  lambda item: (item['circuit_name'], item),
        'cores':  lambda item: (f"core_{item['group_id']}", item),
        'shells': lambda item: (f"shell_{item['group_id']}", item)
    }

    for element, mapping_func in element_mapping.items():
        config_data[element] = {
            key: value for item in data_dict.get("config", {}).get(element, {}).values()
            for key, value in [mapping_func(item)]
        }

    return config_data

def get_lvdt_data(data_dict, data_type: str, flip_sign: bool = False):
    if data_type not in _LVDT_SIGNAL:
        raise ValueError(f"Invalid data type: {data_type}, must be one of {_LVDT_SIGNAL}")
    
    data = {}
    for key, value in data_dict['data'].items():
        if key == 'position':
            data[key] = value
        else:
            complex_data = value[data_type]
            data[key] = {
                data_type: complex_data,
                f"{data_type}_real": complex_data.real,
                f"{data_type}_imag": complex_data.imag,
            }

            abs_data = np.abs(complex_data)
            
            if data_type == 'voltage' and flip_sign:
                n = len(abs_data) // 2
                abs_data[:n] *= -1
                data[key][f"{data_type}_abs"] = abs_data

            data[key][f"{data_type}_abs"] = abs_data
    return data

def get_vc_data(data_dict):
    data = {}
    for key, value in data_dict['data'].items():
        if key == 'position':
            data[key] = value
        else:
            for signal in _VC_SIGNAL:
                data[key] = {signal: value[signal].real}
    return data
###############################################################
#### Define the method to fit the lvdt simulation data     ####
###############################################################

def normalize(pickup_signal, excitation_signal):
    return pickup_signal * excitation_signal

def linear_model(x, a, b):
    return a * x + b

def linear_fit(xdata, ydata, unit = "V", method = "linear-regression"):
    if unit =="mV":
        ydata = ydata * 1000
    
    if method == "linear-regression":
        slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
        return {"slope": slope, "intercept": intercept, "r_value": r_value, "p_value": p_value, "std_err": std_err}
    
    elif method == "curve-fit":
        popt, _ = curve_fit(linear_model, xdata, ydata)
        return {"slope": popt[0], "intercept": popt[1]}

def linear_analysis_RE(xdata, ydata):

    slope, intercept, _, _, _= linregress(xdata, ydata)
    y_pred = slope * xdata + intercept
    y_error = (np.abs(ydata - y_pred) / np.abs(ydata)) * 100

    return {"response":{"slope": slope, "intercept": intercept},
            "predict": y_pred,
            "error": y_error}

def linear_analysis_FS(xdata, ydata):

    slope, intercept, _, _, _= linregress(xdata, ydata)
    y_pred = slope * xdata + intercept
    y_error = (np.abs(ydata - y_pred) / np.abs(ydata)) * 100

    y_range = np.ptp(ydata)
    y_error = (np.abs(ydata - y_pred) / y_range) * 100
    max_error = (np.max(ydata-y_pred) / y_range) * 100

    return {
        'response': {"slope": slope, "intercept": intercept},
        'predict': y_pred, 
        'error': y_error,
        'max_error': max_error
        }

def sensitivity(xdata, ydata):

    params = linear_analysis_FS(xdata, ydata)
    sensitivity = params['response']['slope']
    return sensitivity

def non_linear_index(xdata, ydata):

    params = linear_analysis_FS(xdata, ydata)
    non_linear_index = params['max_error']
    return non_linear_index


###############################################################
#### Define the method to fit the vc simulation data     ######
###############################################################
def quadratic(x, a, b, c):
    return a*x**2 + b*x + c

def quadratic_analysis(xdata, ydata):

    params, _ = curve_fit(quadratic, xdata, ydata)
    predict = quadratic(xdata, *params)
    max_force = np.max(predict)
    max_force_error = 1 - ((predict - max_force)/max_force * 100)

    return {"response": params, 
             "predict": predict, 
             "max_force": max_force,
             "max_force_error": max_force_error}

def max_force(xdata, ydata):

    params = quadratic_analysis(xdata, ydata)
    max_force = params['max_force']
    return max_force

def force_variation_index(xdata, ydata):

    params = quadratic_analysis(xdata, ydata)
    force_variation_index = np.max(params["max_force_error"])
    return force_variation_index


##########################################################
#### Define the method for optimizaiton    ###############
##########################################################

def fitness_function(sensitivity, nonlinear_index, max_force, force_variation_index, s_weight=1, nli_weight=1, mf_weight=1, fvi_weight = 1):
    """
    calculate the fitness function of the data:
    """
    
    fitness = s_weight * sensitivity + nli_weight * nonlinear_index + mf_weight * max_force+ fvi_weight * force_variation_index
    return fitness

##########################################################
#### Define the method for plotting the data    ##########
##########################################################
def plot_lvdt_data(xdata, ydata, unit="V", xlabel=None, ylabel=None, title=None, auto_save=False, fig_size=(8, 6)):
    if unit =="mV":
        ydata = ydata * 1000
    plt.figure(figsize=fig_size)
    plt.plot(xdata, ydata, marker = 'o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    if auto_save:
        plt.savefig(f"{title}.pdf")
    plt.show()

def plot_linear_fit(xdata, ydata, unit="V", xlabel=None, ylabel=None, title=None, auto_save=False, fig_size=(8, 6)):
    if unit =="mV":
        ydata = ydata * 1000
    fit_params = linear_fit(xdata, ydata)
    slope = fit_params["slope"]
    intercept = fit_params["intercept"]
    plt.figure(figsize=fig_size)
    plt.plot(xdata, ydata, marker = 'o', label='Original data')
    plt.plot(xdata, slope * xdata + intercept, 'r', label=f'Fitted data response: {slope:.4f}')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    if auto_save:
        plt.savefig(f"{title}.pdf")
    plt.show()

def plot_linear_fit_error(xdata, ydata, unit="V", title=None, norm=False, auto_save=False, fig_size=(8, 6)):
    if unit =="mV":
        ydata = ydata * 1000
    fit_params = linear_fit(xdata, ydata)
    slope = fit_params["slope"]
    intercept = fit_params["intercept"]
    plt.figure(figsize=fig_size)
    if norm:
        plt.plot(xdata, 100*abs((ydata - (slope * xdata + intercept))/ydata), marker = 'o', label='Fit Error')
        plt.ylabel('Normalized Error %')
    else:
        plt.plot(xdata, ydata - (slope * xdata + intercept), marker = 'o', label='Fit Error')
        plt.ylabel(f"Voltage Error ({unit})")
    plt.title(title)
    plt.xlabel("Position (mm")
    plt.legend()
    plt.grid(True)
    if auto_save:
        plt.savefig(f"{title}.pdf")
    plt.show()

def plot_linear_fit_mutiple(data_dict, unit="V", xlabel=None, ylabel=None, title=None, auto_save=False, fig_size=(8, 6), fit=False):

    plt.figure(figsize=fig_size)
    for key in data_dict.keys():
        xdata = data_dict[key]['position']
        ydata = data_dict[key]['pickup_voltage']
        label = key
        if unit =="mV":
            ydata = ydata * 1000

        fit_params = linear_fit(xdata, ydata)
        slope = fit_params["slope"]
        intercept = fit_params["intercept"]
        if fit:
            plt.plot(xdata, slope * xdata + intercept, marker = 'o', label='Fitted response_' + label)
        else:
            plt.plot(xdata, ydata, marker = 'o', label='simulated response_'+ label)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True)
    if auto_save:
        plt.savefig(f"{title}.pdf")
    plt.show()