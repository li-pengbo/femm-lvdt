import numpy as np
import h5py
import json
import scipy.optimize as opt

class dataHandler:
    def __init__(self):
        pass

    def save_data(self, data, filename):
        with h5py.File(filename, 'w') as f:
            for key, value in data.items():
                f.create_dataset(key, data=value)

    def load_data(self, filename, show_keys=False):
        with h5py.File(filename, "r") as f:
            keys = list(f.keys())
            if show_keys:
                print("Keys: ", keys)
            return {key: f[key][:] for key in f.keys()}
    def data_preprocessing(self, data, show_keys=False):
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
    
    def print_file_keys(self, group=None, data = None, show_all=False):
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
    def get_data(self, file_path, show_keys=False):
        return self.data_preprocessing(self.load_data(file_path, show_keys))
    
    def get_data_from_dict(self, datafolder_path, data_dict, key = None):
        ddict = {}
        if key is None:
            file_keys = list(data_dict.keys())
            for file_key in file_keys:
                filepath = data_dict[file_key]
                ddict[file_key]=self.get_data(datafolder_path + filepath)
            return ddict
        else:
            return self.get_data(datafolder_path + data_dict[key])
    
    def get_data_from_json(self, datafolder_path, jsonfile_path, group_key = None, file_key = None):
        jsonfile = {}
        with open(jsonfile_path) as f:
            jsonfile = json.load(f)
        if group_key is None:
            data = {}
            group_keys = list(jsonfile.keys())
            if "_comment" in group_keys:
                group_keys.remove('_comment')
            for group_key in group_keys:
                data[group_key] = {}
                file_keys = jsonfile[group_key]
                for file_key in file_keys:
                    filepath = jsonfile[group_key][file_key]
                    data[group_key][file_key]=self.get_data(datafolder_path + filepath)
            return data
        file_keys = jsonfile[group_key]
        if file_key:
            if file_key in file_keys:
                filepath = file_keys[file_key]
                return self.data_preprocessing(self.load_data(datafolder_path + filepath))
            else:
                raise ValueError(f"Key {file_key} not found in group {group_key}.")
        else:
            processed_data = {}
            for k, filepath in file_keys.items():
                processed_data[k] = self.get_data(datafolder_path + filepath)
            return processed_data
    
    def print_data_keys(self, data, depth =None, current_depth=0):
        if isinstance(data, dict):
            for key in data:
                print(f"{'  ' * current_depth}{key}") 
                if depth is None or current_depth < depth - 1:
                    self.print_data_keys(data[key], depth, current_depth + 1)
        else:
            pass
    def linfunc(self, x, a, b):
        return a*x + b
    
    def lvdt_fitting(self, linfunc, xdata, ydata, amp_gain = 65, amplification = False, norm_factor = 0.02, normalization = False, ):
        if normalization:
            ydata = ydata * norm_factor
        if amplification:
            ydata = ydata * amp_gain

        popt, pcov = opt.curve_fit(linfunc, xdata, ydata)
        fitted_ydata = linfunc(xdata, *popt)
        return {'response':popt[0], 
                'xdata':xdata, 
                'ydata':ydata, 
                'fitted_ydata':fitted_ydata}