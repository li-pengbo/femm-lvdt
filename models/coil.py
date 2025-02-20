# LVDT_simulation/model/coil.py
import sys
sys.path.append("../")
import femm
import math
from dataclasses import dataclass, field
from models.base import BaseParams, BaseModel
from simulation.material import MaterialHandler as mat_handler
@dataclass
class CoilParams(BaseParams):
    inner_diameter: float                       # Inner diameter (mm)
    bobbin_length: float                        # Bobbin length (mm)
    offset: float                               # Offset (mm)
    wire_diameter: float                        # Wire diameter (mm)
    insulation: float                           # Insulation (mm)
    layers: int                                 # Number of layers

    circuit_name: str = "CoilCircuit"           # Circuit name
    circuit_type: int = 1                       # Circuit type: 0:parallel, 1:series
    circuit_current: float = 1.0                # Circuit current (A)

    upper_pos: float = field(init=False)        # Upper position (mm)
    lower_pos: float = field(init=False)        # Lower position (mm)
    
    wire_pitch: float = field(init=False)       # Wire pitch (mm)
    outer_diameter: float = field(init=False)        # Outer diameter (mm)
    turns_per_layer: float = field(init=False)  # Turns per layer
    total_turns: float = field(init=False)      # Total turns

    def __post_init__(self):
        self.upper_pos = self.offset + self.bobbin_length/2
        self.lower_pos = self.offset - self.bobbin_length/2
        self.wire_pitch = self.wire_diameter + 2*self.insulation
        self.outer_diameter = self.inner_diameter + 2*self.layers*self.wire_pitch
        self.turns_per_layer = math.floor(self.bobbin_length / self.wire_pitch)
        self.total_turns = self.turns_per_layer * self.layers

class CoilModel(BaseModel[CoilParams]):
    def __init__(self, **params):
        super().__init__(CoilParams(**params))

    def _build(self):
            try:
                ri, ro = self._params.inner_diameter/2, self._params.outer_diameter/2
                upper, lower = self._params.upper_pos, self._params.lower_pos
                
                self._make_coil(ri, ro, lower, upper)
                self._set_properties(ri, ro, lower, upper)
                
            except Exception as e:
                error_info = f"coil build failed: {self._params}"
                raise RuntimeError(error_info) from e

    def _make_coil(self, ri, ro, lower, upper):
        femm.mi_drawrectangle(ri, lower, ro, upper)
        femm.mi_addcircprop(self._params.circuit_name, self._params.circuit_current, self._params.circuit_type)
        mat_handler.get_material(self._params.material, self._params.is_customized_material)
        femm.mi_clearselected()

    def _set_properties(self, ri, ro, lower, upper):
        femm.mi_selectrectangle(ri, lower, ro, upper)
        femm.mi_setgroup(self._params.group_id)

        label_pos = ((ro + ri)/2, (upper + lower)/2)
        femm.mi_addblocklabel(*label_pos)
        femm.mi_selectlabel(*label_pos)
        
        femm.mi_setblockprop(
            self._params.material,       # materialname
            self._params.automesh,       # automesh: 0:off, 1:on
            self._params.meshsize,       # meshsize
            self._params.circuit_name,   # circuit name
            self._params.magdir,         # magdir
            self._params.group_id,       # group
            self._params.total_turns     # turns
        )
        femm.mi_clearselected()