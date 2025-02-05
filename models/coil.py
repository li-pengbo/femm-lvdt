# femm_simulator/core/CoilModel.py
import sys
sys.path.append("../")
import femm
import math
from dataclasses import dataclass, field
from models.base import BaseParams, BaseModel
from simulation.material import MaterialHandler as mat_handler
@dataclass
class CoilParams(BaseParams):
    inner_diameter: float                       # 内径 (mm)
    bobbin_length: float                        # 轴向长度 (mm)
    offset: float                               # 位置偏移 (mm)
    wire_diameter: float                        # 线径 (mm)
    insulation: float                           # 绝缘厚度 (mm)
    layers: int                                 # 层数

    circuit_name: str = "CoilCircuit"           # 电路名称
    circuit_type: int = 1                       # 电路串并联模式: 0:并联, 1:串联
    circuit_current: float = 1.0                # 电流 (A)

    upper_pos: float = field(init=False)        # 上端位置 (mm)
    lower_pos: float = field(init=False)        # 下端位置 (mm)
    
    wire_pitch: float = field(init=False)       # 线圈间距 (mm)
    outer_dia: float = field(init=False)        # 外径 (mm)
    turns_per_layer: float = field(init=False)  # 每层匝数
    total_turns: float = field(init=False)      # 总匝数

    def __post_init__(self):
        self.upper_pos = self.offset + self.bobbin_length/2
        self.lower_pos = self.offset - self.bobbin_length/2
        self.wire_pitch = self.wire_diameter + 2*self.insulation
        self.outer_dia = self.inner_diameter + 2*self.layers*self.wire_pitch
        self.turns_per_layer = math.floor(self.bobbin_length / self.wire_pitch)
        self.total_turns = self.turns_per_layer * self.layers

class CoilModel(BaseModel[CoilParams]):
    def __init__(self, **params):
        super().__init__(CoilParams(**params))

    def _build(self):
            try:
                ri, ro = self._params.inner_diameter/2, self._params.outer_dia/2
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