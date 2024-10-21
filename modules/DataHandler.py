import sys
from Helper import *
sys.dont_write_bytecode = True

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

def get_data(group, key=None, data = None):

    if group not in data:
        raise ValueError(f"Group {group} not found in data paths.")

    group_data = data[group]

    if key:
        if key in group_data:
            file_path = group_data[key]
            return process_voltage(load_data(file_path))
        else:
            raise ValueError(f"Key {key} not found in group {group}.")
    else:
        processed_data = {}
        for k, file_path in group_data.items():
            processed_data[k] = process_voltage(load_data(file_path))
        return processed_data
    

def print_data_keys(data, depth =None, current_depth=0):
    if isinstance(data, dict):
        for key in data:
            print(f"{'  ' * current_depth}{key}") 
            if depth is None or current_depth < depth - 1:
                print_data_keys(data[key], depth, current_depth + 1)
    else:
        pass
########################################################################################
LVDT_data_files = {
    "LVDT_aircoil": {
        'aircoil_default': '../data/aircoil/LVDT_aircoil_default.h5',
        'magcore_default': '../data/aircoil/LVDT_magcore_default.h5',
        'combi_default': '../data/aircoil/LVDT_aircoil_magcore_default.h5',},

    "LVDT_alucld_od_08": {
        'alucld_d08d07': '../data/alucld/LVDT_alucld_d08d07_l12.h5',
        'alucld_d08d06': '../data/alucld/LVDT_alucld_d08d06_l12.h5',
        'alucld_d08d05': '../data/alucld/LVDT_alucld_d08d05_l12.h5',
        'alucld_d08d04': '../data/alucld/LVDT_alucld_d08d04_l12.h5',
        },

    "LVDT_alucld_od08_magcore_d04_l06": {
        'alucld_d08d07': '../data/alucld/LVDT_alucld_d08d07_l12_magcore_d04_l06.h5',
        'alucld_d08d06': '../data/alucld/LVDT_alucld_d08d06_l12_magcore_d04_l06.h5',
        'alucld_d08d05': '../data/alucld/LVDT_alucld_d08d05_l12_magcore_d04_l06.h5',
        'alucld_d08d04': '../data/alucld/LVDT_alucld_d08d04_l12_magcore_d04_l06.h5',
        },

    "LVDT_alucld_od_10": {
        'alucld_d10d09': '../data/alucld/LVDT_alucld_d10d09_l12.h5',
        'alucld_d10d08': '../data/alucld/LVDT_alucld_d10d08_l12.h5',
        'alucld_d10d07': '../data/alucld/LVDT_alucld_d10d07_l12.h5',
        'alucld_d10d06': '../data/alucld/LVDT_alucld_d10d06_l12.h5',
        'alucld_d10d05': '../data/alucld/LVDT_alucld_d10d05_l12.h5',
        },
    "LVDT_alucld_od10_magcore_d04_l06": {
        'alucld_d10d09': '../data/alucld/LVDT_alucld_d10d09_l12_magcore_d04_l06.h5',
        'alucld_d10d08': '../data/alucld/LVDT_alucld_d10d08_l12_magcore_d04_l06.h5',
        'alucld_d10d07': '../data/alucld/LVDT_alucld_d10d07_l12_magcore_d04_l06.h5',
        'alucld_d10d06': '../data/alucld/LVDT_alucld_d10d06_l12_magcore_d04_l06.h5',
        'alucld_d10d05': '../data/alucld/LVDT_alucld_d10d05_l12_magcore_d04_l06.h5',
        },

    "LVDT_alucld_od_12": {
        'alucld_d12d11': '../data/alucld/LVDT_alucld_d12d11_l12.h5',
        'alucld_d12d10': '../data/alucld/LVDT_alucld_d12d10_l12.h5',
        'alucld_d12d09': '../data/alucld/LVDT_alucld_d12d09_l12.h5',
        'alucld_d12d08': '../data/alucld/LVDT_alucld_d12d08_l12.h5',
        'alucld_d12d07': '../data/alucld/LVDT_alucld_d12d07_l12.h5',
        'alucld_d12d06': '../data/alucld/LVDT_alucld_d12d06_l12.h5',
        },
    "LVDT_alucld_od12_magcore_d04_l06": {
        'alucld_d12d11': '../data/alucld/LVDT_alucld_d12d11_l12_magcore_d04_l06.h5',
        'alucld_d12d10': '../data/alucld/LVDT_alucld_d12d10_l12_magcore_d04_l06.h5',
        'alucld_d12d09': '../data/alucld/LVDT_alucld_d12d09_l12_magcore_d04_l06.h5',
        'alucld_d12d08': '../data/alucld/LVDT_alucld_d12d08_l12_magcore_d04_l06.h5',
        'alucld_d12d07': '../data/alucld/LVDT_alucld_d12d07_l12_magcore_d04_l06.h5',
        'alucld_d12d06': '../data/alucld/LVDT_alucld_d12d06_l12_magcore_d04_l06.h5',
        },

    "LVDT_alucld_od_14": {
        'alucld_d14d13': '../data/alucld/LVDT_alucld_d14d13_l12.h5',
        'alucld_d14d12': '../data/alucld/LVDT_alucld_d14d12_l12.h5',
        'alucld_d14d11': '../data/alucld/LVDT_alucld_d14d11_l12.h5',
        'alucld_d14d10': '../data/alucld/LVDT_alucld_d14d10_l12.h5',
        'alucld_d14d09': '../data/alucld/LVDT_alucld_d14d09_l12.h5',
        'alucld_d14d08': '../data/alucld/LVDT_alucld_d14d08_l12.h5',
        'alucld_d14d07': '../data/alucld/LVDT_alucld_d14d07_l12.h5',
        },
    "LVDT_alucld_od14_magcore_d04_l06": {
        'alucld_d14d13': '../data/alucld/LVDT_alucld_d14d13_l12_magcore_d04_l06.h5',
        'alucld_d14d12': '../data/alucld/LVDT_alucld_d14d12_l12_magcore_d04_l06.h5',
        'alucld_d14d11': '../data/alucld/LVDT_alucld_d14d11_l12_magcore_d04_l06.h5',
        'alucld_d14d10': '../data/alucld/LVDT_alucld_d14d10_l12_magcore_d04_l06.h5',
        'alucld_d14d09': '../data/alucld/LVDT_alucld_d14d09_l12_magcore_d04_l06.h5',
        'alucld_d14d08': '../data/alucld/LVDT_alucld_d14d08_l12_magcore_d04_l06.h5',
        'alucld_d14d07': '../data/alucld/LVDT_alucld_d14d07_l12_magcore_d04_l06.h5',
        }
}

VC_data_files = {
        "VC_alucld_d08d07": {
        'mag_d07_l04': '../data/alucld/VC_alucld_d08d07_l12_magcore_d07_l04.h5',
        'mag_d07_l06': '../data/alucld/VC_alucld_d08d07_l12_magcore_d07_l06.h5',
        'mag_d07_l08': '../data/alucld/VC_alucld_d08d07_l12_magcore_d07_l08.h5',
        'mag_d07_l10': '../data/alucld/VC_alucld_d08d07_l12_magcore_d07_l10.h5',
        'mag_d07_l12': '../data/alucld/VC_alucld_d08d07_l12_magcore_d07_l12.h5',
        },
    "VC_alucld_d08d06": {
        'mag_d06_l04': '../data/alucld/VC_alucld_d08d06_l12_magcore_d06_l04.h5',
        'mag_d06_l06': '../data/alucld/VC_alucld_d08d06_l12_magcore_d06_l06.h5',
        'mag_d06_l08': '../data/alucld/VC_alucld_d08d06_l12_magcore_d06_l08.h5',
        'mag_d06_l10': '../data/alucld/VC_alucld_d08d06_l12_magcore_d06_l10.h5',
        'mag_d06_l12': '../data/alucld/VC_alucld_d08d06_l12_magcore_d06_l12.h5',
        },
    "VC_alucld_d10d09": {
        'mag_d09_l04': '../data/alucld/VC_alucld_d10d09_l12_magcore_d09_l04.h5',
        'mag_d09_l06': '../data/alucld/VC_alucld_d10d09_l12_magcore_d09_l06.h5',
        'mag_d09_l08': '../data/alucld/VC_alucld_d10d09_l12_magcore_d09_l08.h5',
        'mag_d09_l10': '../data/alucld/VC_alucld_d10d09_l12_magcore_d09_l10.h5',
        'mag_d09_l12': '../data/alucld/VC_alucld_d10d09_l12_magcore_d09_l12.h5',
        },
    "VC_alucld_d10d08": {
        'mag_d08_l04': '../data/alucld/VC_alucld_d10d08_l12_magcore_d08_l04.h5',
        'mag_d08_l06': '../data/alucld/VC_alucld_d10d08_l12_magcore_d08_l06.h5',
        'mag_d08_l08': '../data/alucld/VC_alucld_d10d08_l12_magcore_d08_l08.h5',
        'mag_d08_l10': '../data/alucld/VC_alucld_d10d08_l12_magcore_d08_l10.h5',
        'mag_d08_l12': '../data/alucld/VC_alucld_d10d08_l12_magcore_d08_l12.h5',
        },
}