
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

## Example 
