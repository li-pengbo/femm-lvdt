# LVDT_simulation/models/shell.py
import sys
sys.path.append("../")
import femm
from dataclasses import dataclass, field
from models.base import BaseParams, BaseModel
from core.material import MaterialHandler as mat_handler
@dataclass
class ShellParams(BaseParams):
    inner_diameter: float                       # Shell inner diameter (mm)
    outer_diameter: float                       # Shell outer diameter (mm)
    length: float                               # Shell length (mm)
    offset: float                               # Offset (mm)

    upper_pos: float = field(init=False)        # Upper position (mm)
    lower_pos: float = field(init=False)        # Lower position (mm)

    def __post_init__(self):
        self.upper_pos = self.offset + self.length/2
        self.lower_pos = self.offset - self.length/2

class ShellModel(BaseModel[ShellParams]):
    def __init__(self, **params):
        super().__init__(ShellParams(**params))

    def _build(self):
            try:
                ri, ro = self._params.inner_diameter/2, self._params.outer_diameter/2
                upper, lower = self._params.upper_pos, self._params.lower_pos
                
                self._make_shell(ri, ro, lower, upper)
                self._set_properties(ri, ro, lower, upper)
                
            except Exception as e:
                error_info = f"core build failed: {self._params}"
                raise RuntimeError(error_info) from e


    def _make_shell(self, ri, ro, lower, upper):
        femm.mi_drawrectangle(ri, lower, ro, upper)
        mat_handler.get_material(self._params.material, self._params.is_customized_material)
        femm.mi_clearselected()

    def _set_properties(self, ri, ro, lower, upper):
        femm.mi_selectrectangle(ri, lower, ro, upper)
        femm.mi_setgroup(self._params.group_id)

        label_pos = ((ri+ro)/2, (upper + lower)/2)
        femm.mi_addblocklabel(*label_pos)
        femm.mi_selectlabel(*label_pos)
        
        femm.mi_setblockprop(
            self._params.material,       # materialname
            self._params.automesh,       # automesh
            self._params.meshsize,       # meshsize
            '',                         # circuit
            self._params.magdir,         # magdir
            self._params.group_id,       # group
            0                           # turns
        )
        femm.mi_clearselected()