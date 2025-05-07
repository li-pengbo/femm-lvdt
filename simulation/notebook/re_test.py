import sys
sys.path.append('../../')
import h5py
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from core import data_handler
from core.simulator import SimulatorManager
from core.json_handler import JsonHandler 

sim_manager = SimulatorManager(
    input_jsonname='../config/initial_config/vc_typeA.json', 
    output_filename='vc_result_test.h5', 
    output_dir="../data/typeA", 
    auto_close=False,
    auto_save=True,
    gui = True) 
sim_manager.run_simulation()
