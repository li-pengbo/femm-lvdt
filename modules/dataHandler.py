import numpy as np
import h5py

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
    
def data_preprocessing(data, show_keys=False):
    if 'CC_pos' in data:
        flip_index = len(data['CC_pos'])//2
    voltage_keys = ['CC_volt', 'MC_volt', 'OC_upp_volt', 'OC_low_volt']
    for key in voltage_keys:
        if key in data:
            data[key+'_real'] = data[key].real
            data[key+'_imag'] = data[key].imag
            data[key+'_abs'] = np.abs(data[key])
            data[key+'_abs'][:flip_index] = -data[key+'_abs'][:flip_index]
    if show_keys:
        print("Keys: ", data.keys())
    return data

def print_file_keys(group=None, data = None,  show_all=False):
    if group:
        if group in data:
            print(f"Data group '{group}':")
            for k in data[group]:
                print(f"  {k}")
        else:
            print(f"Data group '{group}' not found.")
    else:
        print("All available data groups:")
        for group_name in data:
            print(f"Data group '{group_name}':")
            if show_all:
                for k in data[group_name]:
                    print(f"  {k}")

def get_data(folder_path, data = None, group = None, key=None, ):

    if group not in data:
        raise ValueError(f"Group {group} not found in data paths.")
    if not group:
        raise ValueError("Group not specified.")
    group_data = data[group]

    if key:
        if key in group_data:
            file_path = group_data[key]
            return data_preprocessing(load_data(folder_path + file_path))
        else:
            raise ValueError(f"Key {key} not found in group {group}.")
    else:
        processed_data = {}
        for k, file_path in group_data.items():
            processed_data[k] = data_preprocessing(load_data(folder_path + file_path))
        return processed_data
    

def print_data_keys(data, depth =None, current_depth=0):
    if isinstance(data, dict):
        for key in data:
            print(f"{'  ' * current_depth}{key}") 
            if depth is None or current_depth < depth - 1:
                print_data_keys(data[key], depth, current_depth + 1)
    else:
        pass