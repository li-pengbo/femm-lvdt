# LVDT_simulation/simulation/simulator.py
import os
import json
import h5py
import logging
import femm
import numpy as np
import random
import uuid
from typing import Dict, Any
from datetime import datetime
from models.base import BaseModel
from models.air import AirModel
from models.coil import CoilModel
from models.core import CoreModel
from models.shell import ShellModel
from core.context import FEMMSession, FEMMError
from core.data_handler import generate_lvdt_data, generate_vc_data
from pprint import pprint
def setup_logging():
    logging.basicConfig(
        filename="simulation.log", level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Simulation Program Started")

class BaseSimulator:
    def __init__(
        self, 
        signal_frequency: float, 
        problem_type: str = 'axi',
        gui: bool = False
    ):
        self.signal_frequency = signal_frequency
        self.problem_type = problem_type
        self.gui = gui
        
        self.session = FEMMSession(
            signal_frequency=self.signal_frequency, 
            problem_type=self.problem_type,
            gui=self.gui
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
            input_jsonname="config.json", 
            output_filename="simulation_results.h5",
            output_dir="results", 
            auto_close=False,
            auto_save=False,
            density_plot=False,
            gui=False
    ):
        self.sim = None
        self.data = None
        self.config = None
        self.input_json = input_jsonname
        self.output_filename = output_filename
        self.output_dir = output_dir

        self.auto_close = auto_close
        self.auto_save = auto_save
        self.density_plot = density_plot
        self.gui = gui

        setup_logging()
        logging.info("=====================================")
        logging.info("Welcome to FEMM SimulatorManager")

        self.load_json_to_dict()
        self.sim = self.create_simulator()
        self.models: Dict[str, BaseModel] = {}
        
    def run_simulation(self):
        self.sim.initialize()
        self.build_models()

        for model in self.models.values():
            if model is not None and hasattr(model, "_build"):
                model._build()

        self.data = self.sim.simulate(self.config)
        self.save_results()
        logging.info("Simulation completed")


        if self.auto_close:
            self.sim.close()
            logging.info("FEMM session closed")
        
        logging.info("=====================================")           
        
    def load_json_to_dict(self):
        with open(self.input_json, "r") as f:
            self.config = json.load(f)
        logging.info("Loaded configuration file")
        
    def save_results(self):
        hdf5_path = os.path.join(self.output_dir, self.output_filename)
        with h5py.File(hdf5_path, "w") as h5f:
            group1 = h5f.create_group("config")
            group2 = h5f.create_group("data")
            self.load_dict_to_h5(h5f, group1, self.config)
            self.load_dict_to_h5(h5f, group2, self.data)
        logging.info(f"Simulation results saved to {hdf5_path}")
    
    def load_dict_to_h5(self, h5file, group, data):
        for key, value in data.items():
            if isinstance(value, dict):
                subgroup = group.create_group(key)
                self.load_dict_to_h5(h5file, subgroup, value)
            elif isinstance(value, list):
                subgroup = group.create_group(key)
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        item_group = subgroup.create_group(f'item_{i}')
                        self.load_dict_to_h5(h5file, item_group, item)
                    else:
                        subgroup.create_dataset(f'item_{i}', data=item)
            else:
                group.create_dataset(key, data=value)

    def create_simulator(self):
            if self.config['simulation']['type'] == "LVDT":
                return LVDTsimulator(
                    signal_frequency=self.config['simulation']['signal_frequency'],
                    output_dir=self.output_dir,
                    output_filename=self.output_filename,
                    auto_save=self.auto_save,
                    density_plot=self.density_plot,
                    gui=self.gui
                )
            elif self.config['simulation']['type'] == "VoiceCoil":
                return VoiceCoilSimulator(
                    signal_frequency=self.config['simulation']['signal_frequency'],
                    output_dir=self.output_dir,
                    output_filename=self.output_filename,
                    auto_save=self.auto_save,
                    density_plot=self.density_plot,
                    gui=self.gui
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
                logging.info(f"Created {len(self.config['coils'])} CoilModels")
            
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

    def __init__(self, signal_frequency, output_dir, output_filename, auto_save = False, density_plot=False,gui=False):
        super().__init__(signal_frequency, problem_type='axi', gui=gui)
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.auto_save = auto_save
        self.density_plot = density_plot
        self.fem_file = None

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
                if self.density_plot:
                    femm.mo_showdensityplot(1, 0, 0.0001, 1.0e-9, "bmag")
                    femm.mo_zoom(-2,-50,50,50)
                    femm.mo_refreshview()

            self.collect_results(lvdt_data, i, coil_names)
            if not self.auto_save:
                self.reset_state()
            self.move_elements(moving_elements, config['simulation']['stepsize'])
        return lvdt_data
        
    def save_state(self):
        femm.mi_zoom(-2,-50,50,50)
        femm.mi_refreshview()
        sim_dir = self.output_dir + '/' + "femm_files"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:12]}"
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)
        self.fem_file = os.path.join(sim_dir, f"lvdt_simulation_{timestamp}.fem")
        femm.mi_saveas(self.fem_file)

    def load_state(self):
        femm.mi_analyze()
        femm.mi_loadsolution()

    def reset_state(self):
        os.remove(self.fem_file)
        os.remove(self.fem_file.replace(".fem", ".ans"))

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

class VoiceCoilSimulator(BaseSimulator):
    def __init__(self, signal_frequency, output_dir, output_filename,auto_save = False, density_plot=False, gui=False):
        super().__init__(signal_frequency, problem_type='axi', gui=gui)
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.auto_save = auto_save
        self.density_plot = density_plot
        self.fem_file = None

    def simulate(self, config: Dict):
        coil_names = [coil['circuit_name'] for coil in config['coils']]
        coil_labels = [coil['group_id'] for coil in config['coils']]

        if 'cores' in config:
            core_labels = [core['group_id'] for core in config['cores']]
        else:
            core_labels = []
        if 'shells' in config:
            shell_labels = [shell['group_id'] for shell in config['shells']]
        else:
            shell_labels = []

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
                if self.density_plot:
                    femm.mo_showdensityplot(1, 0,  0.0001, 1.0e-9, "bmag")
                    femm.mo_zoom(-2,-50,50,50)
                    femm.mo_refreshview()
            self.collect_results(vc_data, i, coil_names, coil_labels, core_labels, shell_labels)
            if not self.auto_save:
                self.reset_state()
            self.move_elements(moving_elements, config['simulation']['stepsize'])
        return vc_data
    
    def save_state(self):
        femm.mi_zoom(-2,-50,50,50)
        femm.mi_refreshview()
        sim_dir = self.output_dir + '/' + "femm_files"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:12]}"
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)
        self.fem_file = os.path.join(sim_dir, f"vc_simulation_{timestamp}.fem")
        femm.mi_saveas(self.fem_file)
    
    def load_state(self):
        femm.mi_analyze()
        femm.mi_loadsolution()
    
    def reset_state(self):
        os.remove(self.fem_file)
        os.remove(self.fem_file.replace(".fem", ".ans"))

    def collect_results(self, vc_data, step, coil_names, coil_labels, core_labels, shell_labels):

        for coil_name, coil_label in zip(coil_names, coil_labels):
            femm.mo_groupselectblock(coil_label)
            coil_force = femm.mo_blockintegral(19)
            vc_data[coil_name]['force'][step] = coil_force

            curr, volt, _ = femm.mo_getcircuitproperties(coil_name)
            if curr != 0:
                resistance = volt / curr
            else:
                resistance = 0
            vc_data[coil_name]['resistance'][step] = resistance
            
            femm.mo_clearblock()
            logging.info(f"{coil_name} - force: {coil_force}")
            logging.info(f"{coil_name} - resistance: {resistance}")

        if core_labels:
            for core in core_labels:
                core_name = f"core_{core}"
                # femm.mo_groupselectblock(core)
                # core_force = femm.mo_blockintegral(19)
                core_force= 0
                vc_data[core_name]['force'][step] = core_force
                # femm.mo_clearblock()
                logging.info(f"{core_name} - force: {core_force}")
                
        if shell_labels:
            for shell in shell_labels:
                shell_name = f"shell_{shell}"
                # femm.mo_groupselectblock(shell)
                # shell_force = femm.mo_blockintegral(19)
                shell_force = 0
                vc_data[shell_name]['force'][step] =  shell_force
                # femm.mo_clearblock()
                logging.info(f"{shell_name} - force: {shell_force}")

    def move_elements(self, moving_elements, stepsize):
        for element in moving_elements:
            femm.mi_selectgroup(element)
        femm.mi_movetranslate(0, stepsize)
        femm.mi_clearselected()