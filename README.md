
## Description
This repository contains Python code using FEMM to simulate the performance of the LVDT (Linear Variable Differential Transformer) and the VC (Voice Coil) actuator.

## Installation

1. Install [FEMM](https://www.femm.info/wiki/Files/files.xml?action=download&file=femm42bin_x64_21Apr2019.exe).

2. Install Miniconda from Windows PowerShell:

   ```Powershell
   curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe -o miniconda.exe
   Start-Process -FilePath ".\miniconda.exe" -ArgumentList "/S" -Wait
   del miniconda.exe
   ```

3. Install the virtual environment:

   ```bash
   conda env create -f environment.yml
   ```

## Usage

This repository contains several folders:

- **data**: Collects all simulation data for analysis and visualization.
- **json**: Stores data file paths to support automated data analysis.
- **modules**: Contains all relevant Python modules for FEMM simulation.
- **simulation**: Holds test code for simulating different design types.
- **visualization**: Contains analysis code to analyze simulation data and visualize results.

The general workflow is:

1. Run the simulation code inside the `simulation` folder.
2. Update the JSON file in the `json` folder with newly added simulation results.
3. Run the analysis code inside the `visualization` folder to analyze and visualize the simulation results.

## Example 

Here is a simple example of how the simulation code works.

1. In this block, the required Python modules are imported:

   ```python
   """
   Author: Pengbo Li
   Created: 2024-10-22
   Version: 1.0

   Description: 
       Simulation of the Corecoil default design created by Fred, inspired by the I2PS LVDT design.
       Check the LVDT performance of the air coil, magnet core, and the combination of both.

   Model:  
   - air coil 
   - magnet core
   - air coil + magnet core

   """
   import sys
   sys.dont_write_bytecode = True
   sys.path.append('../')
   from modules import simulator, coreConfig, geometry
   ```

2. This block provides information necessary for defining parameters:

   ```python
   print(geometry.def_coil_geo.__doc__)
   print(geometry.def_core_geo.__doc__)
   print(geometry.def_cylinder_geo.__doc__)
   ```

3. Define the file path and file name:

   ```python
   path = "../data/aircoil/"
   filename = 'test.h5'
   ```

4. Define the simulation parameters `simulation_params`, core parameters `core_params`, and coil parameters `coil_params` in sequence. You can find a detailed explanation of the parameters by running the code in section 3.

5. After defining all parameters, run this block to start the simulation, and the results will be saved to the predefined path and filename:

   ```python
   simulation_params = {
       'frequency': 10000,
       'amplitude': 0.02,
       'moving_core': coreConfig.moving_config(-5, 1, 10)
   }
   
   core_params = {
       'magnetcore': (8, 4, "N40")
   }
   
   coil_params = {
       'corecoil': ("100um", 0.1, 0, 8, 12, 12, 0),
       'middlecoil': ("100um", 0.1, 0, 16, 3, 18, 0),
       'outercoil': ("100um", 0.1, 0, 16, 3, 18, 16)
   }
   
   simulator.run_lvdt_aircoil_simulation(path, filename, simulation_params, core_params, coil_params)
   ```
