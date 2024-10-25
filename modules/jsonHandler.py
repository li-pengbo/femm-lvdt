import json

def load_parameters_from_json(json_file_path):
    with open(json_file_path, "r") as file:
        data = json.load(file)

    filename = data.get("Filename", "lvdt_simulation_default.h5")
    simulation_freq = data["Excitation"]["Frequency (Hz)"]
    simulation_amplitude = data["Excitation"]["Amplitude (V)"]

    core_params = {
        'Mangetcore': (
            data["Core"]["Magnetcore"]["Diameter (mm)"],
            data["Core"]["Magnetcore"]["Length (mm)"],
            data["Core"]["Magnetcore"]["Material"]
        ),
        'AluminumCylinder': (
            data["Core"]["AluminumCylinder"]["Inner Diameter (mm)"],
            data["Core"]["AluminumCylinder"]["Outer Diameter (mm)"],
            data["Core"]["AluminumCylinder"]["Length (mm)"],
            data["Core"]["AluminumCylinder"]["Material"]
        )
    }

    coil_params = {
        'MiddleCoil': (
            data["Coil"]["MiddleCoil"]["Wire Material"],
            data["Coil"]["MiddleCoil"]["Wire Diameter (mm)"],
            data["Coil"]["MiddleCoil"]["Insulation Thickness (mm)"],
            data["Coil"]["MiddleCoil"]["Layers"],
            data["Coil"]["MiddleCoil"]["Coil Length (mm)"],
            data["Coil"]["MiddleCoil"]["Inner Diameter (mm)"],
            data["Coil"]["MiddleCoil"]["Distance (mm)"]
        ),
        'OuterCoil': (
            data["Coil"]["OuterCoil"]["Wire Material"],
            data["Coil"]["OuterCoil"]["Wire Diameter (mm)"],
            data["Coil"]["OuterCoil"]["Insulation Thickness (mm)"],
            data["Coil"]["OuterCoil"]["Layers"],
            data["Coil"]["OuterCoil"]["Coil Length (mm)"],
            data["Coil"]["OuterCoil"]["Inner Diameter (mm)"],
            data["Coil"]["OuterCoil"]["Distance (mm)"]
        )
    }

    return simulation_freq, simulation_amplitude, core_params, coil_params


