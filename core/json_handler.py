import json
import numpy as np

class JsonHandler:
    def __init__(self, input_json, output_json):
        self.input_json = input_json
        self.json_filename = output_json
        self.config = None
        self.load_config()

    def load_config(self):
        with open(self.input_json, "r") as f:
            self.config = json.load(f)
    
    def save_config(self):
        self.config = self._convert_numpy_to_python(self.config)
        with open(self.json_filename, "w") as f:
            json.dump(self.config, f, indent=4)

    def update_config(self, keys, value):
        temp = self.config
        for key in keys[:-1]:
            if isinstance(temp, dict) and key in temp:
                temp = temp[key]
            elif isinstance(temp, list) and isinstance(key, int) and key < len(temp):
                temp = temp[key]
            else:
                raise KeyError(f"Key path {' -> '.join(map(str, keys))} does not exist!")

        last_key = keys[-1]
        if isinstance(temp, dict) and last_key in temp:
            temp[last_key] = value
        elif isinstance(temp, list) and isinstance(last_key, int) and last_key < len(temp):
            temp[last_key] = value
        else:
            raise KeyError(f"Key path {' -> '.join(map(str, keys))} does not exist!")

    def _convert_numpy_to_python(self, obj):
        if isinstance(obj, dict):
            return {k: self._convert_numpy_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_to_python(v) for v in obj]
        elif isinstance(obj, np.integer):
            return int(obj) 
        elif isinstance(obj, np.floating):
            return float(obj) 
        else:
            return obj 