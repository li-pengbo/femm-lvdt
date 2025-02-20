# LVDT_simulation/simulation/simulator.py
import os
import json
import h5py
import logging
import femm
import numpy as np
from typing import Dict, Any
from datetime import datetime
from models.base import BaseModel
from models.air import AirModel
from models.coil import CoilModel
from models.core import CoreModel
from models.shell import ShellModel
from simulation.context import FEMMSession, FEMMError
from simulation.data_generator import generate_lvdt_data, generate_vc_data

def setup_logging():
    logging.basicConfig(
        filename="../simulation.log", level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Simulation Program Started")

class BaseSimulator:
    def __init__(
        self, 
        signal_frequency: float, 
        problem_type: str = 'axi'
    ):
        self.signal_frequency = signal_frequency
        self.problem_type = problem_type
        
        self.session = FEMMSession(
            signal_frequency=self.signal_frequency, 
            problem_type=self.problem_type
        )

    def initialize(self):
        try:
            self.session.open()
            logging.info("FEMM session initialized")
        except FEMMError as e:
            logging.error(f"initialization failed: {str(e)}")
            raise e

    def simulate(self) -> None:
        raise NotImplementedError("simulate method is not implemented, please implement it in subclass")
    
    def close(self) -> None:
        self.session.close()
        logging.info("FEMM session closed")

class SimulatorManager:
    def __init__(
            self, 
            input_config_json="config.json", 
            output_dir="results", 
            output_config_json="simulation_config.json", 
            output_data_hdf5="simulation_results.h5",
            auto_close=False,
    ):
        self.config = None
        self.config_path = input_config_json
        self.output_dir = output_dir
        self.json_filename = output_config_json
        self.hdf5_filename = output_data_hdf5
        self.auto_close = auto_close

        setup_logging()
        logging.info("=====================================")
        logging.info("Welcome to FEMM SimulatorManager")

        self.load_config()
        self.sim = self.create_simulator()
        self.models: Dict[str, BaseModel] = {}
        
    def run_simulation(self):
        self.sim.initialize()
        self.build_models()
        self.save_config_json()

        for model in self.models.values():
            if model is not None and hasattr(model, "_build"):
                model._build()
        self.sim.simulate(self.config)
        logging.info("Simulation completed")

        if self.auto_close:
            self.sim.close()
            logging.info("FEMM session closed")
        
        logging.info("=====================================")           
        
    def load_config(self):
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
        logging.info("Loaded configuration file")

    def save_config_json(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        json_path = os.path.join(self.output_dir, self.json_filename)
        with open(json_path, "w") as f:
            json.dump(self.config, f, indent=4)
        logging.info(f"Configuration saved to {json_path}")

    def create_simulator(self):
            if self.config['simulation']['type'] == "LVDT":
                return LVDTsimulator(
                    signal_frequency=self.config['simulation']['signal_frequency'],
                    output_dir=self.output_dir,
                    hdf5_filename=self.hdf5_filename
                )
            elif self.config['simulation']['type'] == "VoiceCoil":
                return VoiceCoilSimulator(
                    signal_frequency=self.config['simulation']['signal_frequency'],
                    output_dir=self.output_dir,
                    hdf5_filename=self.hdf5_filename
                )
            else:
                raise ValueError("Unsupported simulation type")
            
    def build_models(self):
        try:
            if 'air_space' in self.config:
                self.models['airspace'] = AirModel(**self.config['air_space'])
                logging.info("AirModel created")
            
            if 'coils' in self.config and isinstance(self.config['coils'], list):
                for i, coil_params in enumerate(self.config['coils'], start=1):
                    key = f"coil_{i}"
                    self.models[key] = CoilModel(**coil_params)
                    self.config['coils'][i-1] = self.models[key].get_params
                logging.info("CoilModels created")
            
            if 'cores' in self.config and isinstance(self.config['cores'], list):
                for i, core_params in enumerate(self.config['cores'], start=1):
                    key = f"cores_{i}"
                    self.models[key] = CoreModel(**core_params)
                    self.config['cores'][i-1] = self.models[key].get_params
                logging.info(f"Created {len(self.config['cores'])} CoreModels")
            
            if 'shells' in self.config and isinstance(self.config['shells'], list):
                for i, shell_params in enumerate(self.config['shells'], start=1):
                    key = f"shells_{i}"
                    self.models[key] = ShellModel(**shell_params)
                    self.config['shells'][i-1] = self.models[key].get_params
                logging.info(f"Created {len(self.config['shells'])} ShellModels")

            logging.info("All models created")
        except Exception as e:
            logging.error(f"Error while building models: {str(e)}")
            raise

class LVDTsimulator(BaseSimulator):

    def __init__(self, signal_frequency, output_dir, hdf5_filename):
        super().__init__(signal_frequency)
        self.output_dir = output_dir
        self.hdf5_filename = hdf5_filename

    def simulate(self, config: Dict):
        coil_names = [coil['circuit_name'] for coil in config['coils']]
        moving_elements = config["simulation"]["moving_elements"]
        lvdt_data = generate_lvdt_data(config)

        for element in moving_elements:
            femm.mi_selectgroup(element)
        femm.mi_movetranslate(0, config['simulation']['initial_position'])
        femm.mi_clearselected()
    
        for i in range(config['simulation']['steps']+1):
            logging.info(f"iteration {i}/{config['simulation']['steps']}")
            logging.info(f"position: {lvdt_data['position'][i]}")
            self.save_state()
            self.load_state()
            
            if lvdt_data['position'][i] == 0:
                femm.mo_showdensityplot(1,0.0001, 0.0001, 1.0e-9, "bmag")
                femm.mo_zoom(-2,-50,50,50)
                femm.mo_refreshview()

            self.collect_results(lvdt_data, i, coil_names)
            self.move_elements(moving_elements, config['simulation']['stepsize'])
        self.save_results(lvdt_data)
        
    def save_state(self):
        femm.mi_zoom(-2,-50,50,50)
        femm.mi_refreshview()
        sim_dir = self.output_dir + '/' + "femm_files"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)
        femm.mi_saveas(os.path.join(sim_dir, f"lvdt_simulation_{timestamp}.fem"))

    def load_state(self):
        femm.mi_analyze()
        femm.mi_loadsolution()

    def collect_results(self, lvdt_data, step, coil_names):
        for coil in coil_names:
            curr, volt, flux = femm.mo_getcircuitproperties(coil)
            lvdt_data[coil]['current'][step] = curr
            lvdt_data[coil]['voltage'][step] = volt
            lvdt_data[coil]['flux'][step] = flux
            logging.info(f"{coil} - current: {curr}, voltage: {volt}, flux: {flux}")
            
    def move_elements(self, moving_elements, stepsize):
        for element in moving_elements:
            femm.mi_selectgroup(element)
        femm.mi_movetranslate(0, stepsize)
        femm.mi_clearselected()

    def save_results(self, lvdt_data):
        hdf5_path = os.path.join(self.output_dir, self.hdf5_filename)
        with h5py.File(hdf5_path, "a") as f:
            for key, data_dict in lvdt_data.items():
                if isinstance(data_dict, dict):
                    for sub_key, value in data_dict.items():
                        dataset_name = f"{key}/{sub_key}"
                        if dataset_name in f:
                            del f[dataset_name]  
                        f.create_dataset(dataset_name, data=np.array(value))
                else:
                    if key in f:
                        del f[key]  
                    f.create_dataset(key, data=np.array(data_dict))
        logging.info(f"LVDT simulation results saved to {hdf5_path}")

#TODO: Implement VoiceCoilSimulator
class VoiceCoilSimulator(BaseSimulator):
    def __init__(self, signal_frequency, output_dir, hdf5_filename):
        super().__init__(signal_frequency)
        self.output_dir = output_dir
        self.hdf5_filename = hdf5_filename
    
    def simulate(self, config: Dict):
        coil_names = [coil['circuit_name'] for coil in config['coils']]
        coil_labels = [coil['group_id'] for coil in config['coils']]
        core_labels = [core['group_id'] for core in config['cores']]
        shell_labels = [shell['group_id'] for shell in config['shells']]
        moving_elements = config["simulation"]["moving_elements"]
        vc_data = generate_vc_data(config)

        for element in moving_elements:
            femm.mi_selectgroup(element)
        femm.mi_movetranslate(0, config['simulation']['initial_position'])
        femm.mi_clearselected()
    
        for i in range(config['simulation']['steps']+1):
            logging.info(f"iteration {i}/{config['simulation']['steps']}")
            logging.info(f"position: {vc_data['position'][i]}")
            self.save_state()
            self.load_state()
            
            if vc_data['position'][i] == 0:
                femm.mo_showdensityplot(1,0.0001, 0.0001, 1.0e-9, "bmag")
                femm.mo_zoom(-2,-50,50,50)
                femm.mo_refreshview()

            self.collect_results(vc_data, i, coil_names, coil_labels, core_labels, shell_labels)
            self.move_elements(moving_elements, config['simulation']['stepsize'])
        self.save_results(vc_data)

    def save_state(self):
        femm.mi_zoom(-2,-50,50,50)
        femm.mi_refreshview()
        sim_dir = self.output_dir + '/' + "vc_files"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)
        femm.mi_saveas(os.path.join(sim_dir, f"vc_simulation_{timestamp}.fem"))
    
    def load_state(self):
        femm.mi_analyze()
        femm.mi_loadsolution()

    def collect_results(self, vc_data, step, coil_names, coil_labels, core_labels, shell_labels):
        for coil_name, coil_label in zip(coil_names, coil_labels):
            femm.mo_groupselectblock(coil_label)
            force = femm.mo_blockintegral(19)
            vc_data[coil_name]['force'][step] = force
            femm.mo_clearblock()
            logging.info(f"{coil_name} - force: {force}")

        for core in core_labels:
            core_name = "core_" + str(core)
            femm.mo_groupselectblock(core)
            force = femm.mo_blockintegral(19)
            vc_data[core_name]['force'][step] = force
            femm.mo_clearblock()
            logging.info(f"{core_name} - force: {force}")

        for shell in shell_labels:
            shell_name = "shell_" + str(shell)
            femm.mo_groupselectblock(shell)
            force = femm.mo_blockintegral(19)
            vc_data[shell_name]['force'][step] = force
            femm.mo_clearblock()
            logging.info(f"{shell_name} - force: {force}")

    def move_elements(self, moving_elements, stepsize):
        for element in moving_elements:
            femm.mi_selectgroup(element)
        femm.mi_movetranslate(0, stepsize)
        femm.mi_clearselected()

    def save_results(self, vc_data):
        hdf5_path = os.path.join(self.output_dir, self.hdf5_filename)
        with h5py.File(hdf5_path, "a") as f:
            for key, data_dict in vc_data.items():
                if isinstance(data_dict, dict):
                    for sub_key, value in data_dict.items():
                        dataset_name = f"{key}/{sub_key}"
                        if dataset_name in f:
                            del f[dataset_name]  
                        f.create_dataset(dataset_name, data=np.array(value))
                else:
                    if key in f:
                        del f[key]  
                    f.create_dataset(key, data=np.array(data_dict))
        logging.info(f"Voice Coil simulation results saved to {hdf5_path}")    